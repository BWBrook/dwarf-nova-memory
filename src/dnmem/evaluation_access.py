"""Pure pre-request authorization checks for the protected evaluation block."""

import hashlib
import json
from pathlib import Path

from .evaluation import PARAMETER_SHA256,START,STOP


def require_authorization(path,freeze,protocol_path):
    path=Path(path)
    if not path.is_file():raise PermissionError('Barry has not authorized evaluation access')
    record=json.loads(path.read_text())
    protocol_hash=hashlib.sha256(Path(protocol_path).read_bytes()).hexdigest()
    if (record.get('status')!='authorized' or record.get('approved_by')!='Barry W. Brook'
            or not str(record.get('approval_verbatim','')).strip()
            or record.get('freeze_commit')!=freeze or record.get('protocol_sha256')!=protocol_hash
            or record.get('parameters_sha256')!=PARAMETER_SHA256
            or record.get('start_jd')!=START or record.get('stop_jd')!=STOP):
        raise PermissionError('authorization does not match the frozen evaluation scope')
    if record.get('timestamp_mode') not in ('git','zenodo'):
        raise PermissionError('the protocol timestamp choice is not recorded')
    if record['timestamp_mode']=='zenodo' and not record.get('zenodo_doi'):
        raise PermissionError('the selected external timestamp is not deposited')
    return record
