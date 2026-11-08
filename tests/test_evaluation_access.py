import json,hashlib,tempfile,unittest
from pathlib import Path
from dnmem.evaluation_access import require_authorization
from dnmem.evaluation import PARAMETER_SHA256,START,STOP
from dnmem.evaluation_acquire import calendar_windows


class ProtectedAccessTests(unittest.TestCase):
    def test_authority_must_explicitly_match_the_frozen_scope(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);authority=root/'authorization.json';protocol=root/'protocol.md';protocol.write_text('synthetic protocol')
            with self.assertRaises(PermissionError):require_authorization(authority,'freeze',protocol)
            r={'status':'authorized','approved_by':'Barry W. Brook','approval_verbatim':'Synthetic fixture only',
               'freeze_commit':'freeze','protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),
               'parameters_sha256':PARAMETER_SHA256,'start_jd':START,'stop_jd':STOP,'timestamp_mode':'git'}
            authority.write_text(json.dumps(r));require_authorization(authority,'freeze',protocol)
            r['stop_jd']+=1;authority.write_text(json.dumps(r))
            with self.assertRaises(PermissionError):require_authorization(authority,'freeze',protocol)
            r['stop_jd']=STOP;r['timestamp_mode']='zenodo';authority.write_text(json.dumps(r))
            with self.assertRaises(PermissionError):require_authorization(authority,'freeze',protocol)

    def test_request_plan_cannot_request_2018(self):
        windows=calendar_windows()
        self.assertEqual(len(windows),59)
        self.assertEqual(windows[0],(2436934.,START))
        self.assertTrue(all(lo<hi<STOP and hi-lo<=366 for lo,hi in windows))
        self.assertTrue(all(windows[i][1]==windows[i+1][0] for i in range(len(windows)-2)))


if __name__=='__main__':unittest.main()
