from __future__ import annotations

import html
import json
import logging
import re
from typing import Any
from typing import Optional
from urllib import parse as urllib_parse
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

from django.conf import settings
from django.db import transaction

from .models import Job

logger = logging.getLogger(__name__)
HTML_TAG_RE = re.compile(r'<[^>]+>')


class JoinSyncError(RuntimeError):
    pass


def _clean_text(value: Any) -> str:
    if value is None:
        return ''
    text = html.unescape(str(value))
    text = HTML_TAG_RE.sub(' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def _extract_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        for key in ('data', 'results', 'items', 'jobs'):
            items = payload.get(key)
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]

    return []


def _request_json(url: str, *, params: Optional[dict[str, Any]] = None) -> Any:
    query_string = urllib_parse.urlencode(params or {})
    request_url = f'{url}?{query_string}' if query_string else url

    headers = {
        'Accept': 'application/json',
    }

    if settings.JOIN_API_TOKEN:
        headers['Authorization'] = settings.JOIN_API_TOKEN

    request = urllib_request.Request(
        request_url,
        headers=headers,
        method='GET',
    )

    try:
        with urllib_request.urlopen(request, timeout=settings.JOIN_API_TIMEOUT) as response:
            payload = response.read().decode('utf-8')
            return json.loads(payload)
    except HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='ignore') if hasattr(exc, 'read') else str(exc)
        raise JoinSyncError(f'JOIN API HTTPError {exc.code}: {detail}') from exc
    except URLError as exc:
        raise JoinSyncError(f'JOIN API network error: {exc.reason}') from exc
    except json.JSONDecodeError as exc:
        raise JoinSyncError('JOIN API returned invalid JSON.') from exc


def _derive_location_choice(job_data: dict[str, Any]) -> str:
    workplace_type = str(job_data.get('workplaceType') or job_data.get('workplace_type') or '').upper()
    remote_flag = bool(job_data.get('remote'))

    office = job_data.get('office')
    office_text = ''
    if isinstance(office, dict):
        office_text = ' '.join(
            str(office.get(field, ''))
            for field in ('name', 'city', 'country', 'address')
        )
    elif office is not None:
        office_text = str(office)

    office_text_lower = office_text.lower()

    if workplace_type == 'HYBRID':
        return 'remote-hybrid'
    if workplace_type == 'REMOTE' or remote_flag:
        return 'remote'
    if 'abuja' in office_text_lower:
        return 'abuja'
    if 'uyo' in office_text_lower:
        return 'uyo'

    return 'uyo'


def _derive_job_type_choice(job_data: dict[str, Any]) -> str:
    employment_type = job_data.get('employmentType') or job_data.get('employment_type') or job_data.get('employmentTypeName') or ''
    if isinstance(employment_type, dict):
        employment_type = employment_type.get('name') or employment_type.get('title') or employment_type.get('label') or ''

    employment_text = str(employment_type).lower()

    if 'part' in employment_text:
        return 'part-time'
    if 'contract' in employment_text:
        return 'contract'
    if 'intern' in employment_text:
        return 'internship'

    return 'full-time'


def _derive_public_url(job_data: dict[str, Any]) -> str:
    for key in ('url', 'publicUrl', 'public_url', 'applicationUrl', 'application_url', 'jobUrl', 'job_url'):
        value = job_data.get(key)
        if value:
            return str(value)
    return ''


def _map_join_job(job_data: dict[str, Any]) -> dict[str, Any]:
    title = _clean_text(job_data.get('title') or job_data.get('name') or f"JOIN Job {job_data.get('id', '')}")
    description = _clean_text(job_data.get('description') or job_data.get('content') or job_data.get('summary') or '')
    requirements = _clean_text(job_data.get('requirements') or job_data.get('responsibilities') or description or 'See the full JOIN job posting for details.')
    source_status = str(job_data.get('status') or 'ONLINE').upper()

    return {
        'title': title,
        'location': _derive_location_choice(job_data),
        'job_type': _derive_job_type_choice(job_data),
        'description': description or 'See the full JOIN job posting for role details.',
        'requirements': requirements or 'See the full JOIN job posting for role details.',
        'is_featured': source_status == 'ONLINE',
        'join_com_url': _derive_public_url(job_data) or None,
        'source_status': source_status,
        'raw_data': job_data,
    }


def fetch_join_jobs() -> list[dict[str, Any]]:
    if not settings.JOIN_API_TOKEN:
        return []

    jobs: list[dict[str, Any]] = []
    page = 1
    page_size = 50

    while True:
        payload = _request_json(
            f'{settings.JOIN_API_BASE_URL.rstrip("/")}/jobs',
            params={
                'status': 'ONLINE,OFFLINE,ARCHIVED',
                'content': 'true',
                'page': page,
                'pageSize': page_size,
                'sort': '-createdAt',
            },
        )
        items = _extract_items(payload)
        jobs.extend(items)

        if len(items) < page_size:
            break

        page += 1
        if page > 20:
            break

    return jobs


@transaction.atomic
def sync_join_jobs(*, delete_missing: bool = True) -> dict[str, int]:
    join_jobs = fetch_join_jobs()
    if not join_jobs:
        return {
            'fetched': 0,
            'created_or_updated': 0,
            'deleted': 0,
        }

    external_ids: set[str] = set()
    created_or_updated = 0

    for job_data in join_jobs:
        external_id = str(job_data.get('id') or job_data.get('externalId') or job_data.get('external_id') or '').strip()
        if not external_id:
            logger.warning('Skipping JOIN job without an external id: %s', job_data)
            continue

        defaults = _map_join_job(job_data)
        Job.objects.update_or_create(
            external_id=external_id,
            defaults=defaults,
        )
        external_ids.add(external_id)
        created_or_updated += 1

    deleted = 0
    if delete_missing:
        deleted, _ = Job.objects.filter(external_id__isnull=False).exclude(external_id__in=external_ids).delete()

    return {
        'fetched': len(join_jobs),
        'created_or_updated': created_or_updated,
        'deleted': deleted,
    }
