import csv
from contextlib import redirect_stdout
import importlib.util
import io
import json
import math
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dnmem import g3a_acquisition as acquisition

NAME, AUID = "SS Aur", "001-TST-001"
FIELDS = ["obsID", "JD", "mag", "uncert", "fainterThan", "band", "by", "val"]


def row(identifier="synthetic-1", jd=150., **changes):
    value = dict(obsID=identifier, JD=str(jd), mag="10.25", uncert="None",
                 fainterThan="0", band="Vis.", by="SYNTHETIC", val="V")
    value.update(changes)
    return value


def native(rows=None, *, name=NAME, auid=AUID, count=None, fields=FIELDS):
    root = ET.Element("Object")
    ET.SubElement(root, "Name").text = name
    ET.SubElement(root, "AUID").text = auid
    if count is not None:
        ET.SubElement(root, "Count").text = str(count)
    if rows is not None:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        ET.SubElement(root, "Data").text = output.getvalue()
    return ET.tostring(root)


def parse(payload, start=100., end=200., page=1):
    return acquisition.parse_page(payload, NAME, AUID, start, end, page)


def executor_module():
    spec = importlib.util.spec_from_file_location("g3a_execute_offline_test", ROOT / "scripts/g3a_execute.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_receipt(label):
    return dict(native_file=label + ".xml", sha256="0" * 64, source_url="synthetic-only")


class G3aNativeBoundaryTests(unittest.TestCase):
    def test_authorized_date_and_target_registry_are_fixed(self):
        self.assertEqual(acquisition.STOP, 2447892.5)
        self.assertEqual(acquisition.END, math.nextafter(2447892.5, -math.inf))
        self.assertEqual(acquisition.TARGETS,
                         ("SS Aur", "RU Peg", "AR And", "X Leo", "TW Vir", "UU Aql",
                          "CH UMa", "DX And", "U Gem", "IP Peg"))

    def test_wrong_name_and_resolved_auid_are_rejected_before_rows(self):
        for payload in (native([row()], name="RU Peg"), native([row()], auid="001-TST-002"),
                        native([row()], auid="unresolved")):
            with self.subTest(payload=payload), self.assertRaisesRegex(ValueError, "identity"):
                parse(payload)

    def test_unapproved_identity_cannot_be_resolved(self):
        with self.assertRaisesRegex(ValueError, "unapproved"):
            acquisition.identity(native(name="SS Cyg"), "SS Cyg")

    def test_reserved_row_rejects_whole_page_before_any_summary(self):
        for jd in (acquisition.STOP, math.nextafter(acquisition.STOP, math.inf), float("nan")):
            with self.subTest(jd=jd), self.assertRaisesRegex(ValueError, "before any summaries"):
                parse(native([row("permitted", acquisition.END - 1), row("forbidden", jd)]),
                      start=acquisition.END - 2, end=acquisition.END)

    def test_invalid_window_is_checked_before_parsing_payload(self):
        with self.assertRaisesRegex(ValueError, "before 1990"):
            parse(b"not XML", start=100., end=acquisition.STOP)

    def test_both_native_date_endpoints_are_inclusive(self):
        original = [row("first", 100.), row("last", 200.)]
        rows, metadata = parse(native(original))
        self.assertEqual(rows, original)
        self.assertFalse(metadata["continue"])

    def test_count_marker_requires_continuation_even_below_cap(self):
        rows, metadata = parse(native([row()], count=1))
        self.assertEqual(len(rows), 1)
        self.assertEqual(metadata, {"continue":True, "termination":"continuation_marker"})

    def test_terminal_no_data_requires_previous_page_or_explicit_zero(self):
        with self.assertRaisesRegex(ValueError, "does not establish an empty archive"):
            parse(native())
        for payload, page, termination in ((native(count=0), 1, "explicit_zero"),
                                           (native(), 2, "no_data_after_page")):
            with self.subTest(page=page):
                rows, metadata = parse(payload, page=page)
                self.assertEqual(rows, [])
                self.assertEqual(metadata, {"continue":False, "termination":termination})

    def test_marker_and_csv_contradictions_are_rejected(self):
        for payload in (native([], count=2), native([row()], count=0), native([row()], count=-1)):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                parse(payload)

    def test_empty_csv_with_zero_count_retains_explicit_terminal_evidence(self):
        rows, metadata = parse(native([], count=0))
        self.assertEqual(rows, [])
        self.assertEqual(metadata, {"continue":False, "termination":"explicit_zero"})

    def test_duplicate_observation_ids_in_a_page_are_rejected(self):
        for second in (row(), row(mag="10.75")):
            with self.subTest(second=second), self.assertRaisesRegex(ValueError, "duplicate"):
                parse(native([row(), second]))

    def test_inclusive_window_duplicates_are_deduplicated_but_conflicts_stop(self):
        first, second = row("early", 100.), row("endpoint", 200.)
        rows, duplicates = acquisition.combine_rows([[second], [first, dict(second)]])
        self.assertEqual(rows, [first, second])
        self.assertEqual(duplicates, 1)
        for changes in (dict(mag="11.0"), dict(uncert="0.2"), dict(fainterThan="1")):
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, "conflicting"):
                acquisition.combine_rows([[second], [{**second, **changes}]])

    def test_none_uncertainty_and_fainter_than_limit_stay_literal(self):
        original = [row(), row("limit", 151., mag="14.50", fainterThan="1", uncert="")]
        rows, _ = parse(native(original))
        self.assertEqual(rows, original)
        self.assertEqual(rows[0]["uncert"], "None")
        self.assertEqual(rows[1]["fainterThan"], "1")
        self.assertEqual(rows[1]["mag"], "14.50")

    def test_malformed_schema_and_short_or_long_records_are_rejected(self):
        payloads = [native([row()], fields=FIELDS + ["JD"]),
                    native([{k:v for k,v in row().items() if k != "uncert"}], fields=[k for k in FIELDS if k != "uncert"])]
        ordinary = native([row()]).decode()
        payloads.extend([ordinary.replace("synthetic-1,150.0", "synthetic-1,extra,150.0").encode(),
                         ordinary.replace(",SYNTHETIC,V", ",SYNTHETIC").encode()])
        for payload in payloads:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                parse(payload)

    def test_invalid_numerics_and_limit_flags_do_not_become_measurements(self):
        for changes in (dict(mag="nan"), dict(uncert="inf"), dict(uncert="-0.1"),
                        dict(fainterThan="True"), dict(by=""), dict(band="")):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                parse(native([row(**changes)]))

    def test_cap_without_marker_requires_subdivision_not_success(self):
        with patch.object(acquisition, "ROW_CAP", 2):
            payload = native([row("one", 120.), row("two", 180.)])
            with self.assertRaises(acquisition.UncertainCap):
                parse(payload)
            rows, metadata = parse(native([row("one", 120.), row("two", 180.)], count=2))
            self.assertEqual(len(rows), 2)
            self.assertTrue(metadata["continue"])

    def test_url_registry_bounds_and_identity_parameters_are_explicit(self):
        for name in acquisition.TARGETS:
            url = urlsplit(acquisition.request_url(name, 100., acquisition.END, auid=AUID, page=2))
            query = parse_qs(url.query, keep_blank_values=True)
            self.assertEqual((url.scheme, url.netloc, url.path), ("https", "vsx.aavso.org", "/index.php"))
            self.assertEqual(query["ident"], [AUID])
            self.assertEqual(query["page"], ["2"])
            self.assertEqual(float(query["fromjd"][0]), 100.)
            self.assertEqual(float(query["tojd"][0]), acquisition.END)
            self.assertLess(float(query["tojd"][0]), acquisition.STOP)
        metadata = parse_qs(urlsplit(acquisition.request_url(NAME, 100., 200., metadata=True)).query)
        self.assertEqual(metadata["data"], ["0"])
        self.assertEqual(metadata["ident"], [NAME])

    def test_unapproved_targets_nonfinite_windows_and_invalid_pagination_are_blocked(self):
        for name in ("SS Cyg", "Z Cam", "SS Aur&tojd=9999999", "ss aur"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                acquisition.request_url(name, 100., 200.)
        for start, end in ((0., 200.), (200., 100.), (100., 100.), (100., acquisition.STOP),
                           (float("nan"), 200.), (100., float("inf"))):
            with self.subTest(start=start,end=end), self.assertRaises(ValueError):
                acquisition.request_url(NAME, start, end)
        for page in (0, 101, 1.5, "2", True):
            with self.subTest(page=page), self.assertRaises(ValueError):
                acquisition.request_url(NAME, 100., 200., page=page)
        for auid in ("", "001-tst-001", "001-TST-001&tojd=9999999"):
            with self.subTest(auid=auid), self.assertRaises(ValueError):
                acquisition.request_url(NAME, 100., 200., auid=auid)

    def test_declared_request_windows_cover_development_only_with_shared_endpoints(self):
        windows = acquisition.request_windows()
        self.assertEqual(windows[0][0], 1.)
        self.assertEqual(windows[-1][1], acquisition.END)
        for i,(start,end) in enumerate(windows):
            self.assertLess(start,end)
            self.assertLess(end,acquisition.STOP)
            if i:
                self.assertEqual(windows[i-1][1],start)


class G3aOfflineExecutionBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.execute = executor_module()

    def test_reserved_row_cannot_reach_acquisition_summary(self):
        responses = [native(), native([row(jd=acquisition.STOP)])]
        calls = []
        def fetch(url,directory,label):
            calls.append(url)
            return responses[len(calls)-1],fake_receipt(label)
        with tempfile.TemporaryDirectory() as tmp, patch.object(self.execute,"fetch",side_effect=fetch), \
                patch.object(self.execute,"request_windows",return_value=[(100.,200.)]):
            directory = Path(tmp)/"ss-aur"
            with self.assertRaisesRegex(ValueError,"before any summaries"):
                self.execute.acquire_star(dict(name=NAME),directory)
            self.assertFalse((directory/"acquisition.json").exists())
            self.assertEqual(len(calls),2)

    def test_metadata_with_observations_is_a_fatal_scope_violation(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(self.execute,"fetch",return_value=(native([row(jd=2447892.5)]),fake_receipt("identity"))) as fetch:
            directory=Path(tmp)/"ss-aur"
            with self.assertRaises(acquisition.ScopeViolation):
                self.execute.acquire_star(dict(name=NAME),directory)
            self.assertEqual(fetch.call_count,1)
            self.assertFalse((directory/"acquisition.json").exists())

    def test_pagination_is_followed_until_terminal_and_overlap_is_deduplicated(self):
        responses = [native(), native([row("shared",200.)],count=1), native(),
                     native([row("shared",200.),row("later",250.)])]
        calls = []
        def fetch(url,directory,label):
            calls.append(url)
            return responses[len(calls)-1],fake_receipt(label)
        with tempfile.TemporaryDirectory() as tmp, patch.object(self.execute,"fetch",side_effect=fetch), \
                patch.object(self.execute,"request_windows",return_value=[(100.,200.),(200.,300.)]):
            selected, metadata = self.execute.acquire_star(dict(name=NAME),Path(tmp)/"ss-aur")
            self.assertEqual([r["obsID"] for r in selected],["shared","later"])
            self.assertEqual(metadata["duplicate_endpoint_rows"],1)
        self.assertEqual([parse_qs(urlsplit(url).query).get("page", ["metadata"]) for url in calls],
                         [["metadata"],["1"],["2"],["1"]])

    def test_cap_subdivision_never_widens_approved_window(self):
        calls = []
        def fetch(url,directory,label):
            query=parse_qs(urlsplit(url).query)
            calls.append(query)
            start,end=float(query["fromjd"][0]),float(query["tojd"][0])
            if query["data"] == ["0"]:
                payload=native()
            elif (start,end)==(100.,200.):
                payload=native([row("first",100.),row("last",200.)])
            else:
                payload=native([row("first",100.)] if start==100. else [row("last",200.)])
            return payload,fake_receipt(label)
        with tempfile.TemporaryDirectory() as tmp, patch.object(self.execute,"fetch",side_effect=fetch), \
                patch.object(self.execute,"request_windows",return_value=[(100.,200.)]), \
                patch.object(acquisition,"ROW_CAP",2):
            selected,_=self.execute.acquire_star(dict(name=NAME),Path(tmp)/"ss-aur")
            self.assertEqual([r["obsID"] for r in selected],["first","last"])
            actual=[(float(q["fromjd"][0]),float(q["tojd"][0])) for q in calls[1:]]
            self.assertEqual(actual,[(100.,200.),(100.,150.),(150.,200.)])

    def test_redirect_is_refused_without_following_target(self):
        with self.assertRaisesRegex(acquisition.ScopeViolation,"redirect refused"):
            self.execute.NoRedirect().redirect_request(None,None,302,"redirect",{},"https://example.invalid/unbounded")

    def test_scope_violation_aborts_whole_execution_before_next_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve()
            config=root/"config.json"
            config.write_text(json.dumps(dict(stop_jd_exclusive=2447892.5,
                              stars=[dict(name=name,slug=name.lower().replace(" ","-")) for name in acquisition.TARGETS])))
            (root/"data/access").mkdir(parents=True)
            (root/"data/access/g3a_authority.json").write_text(json.dumps(dict(
                status="approved_for_frozen_execution",targets=list(acquisition.TARGETS),stop_jd_exclusive=2447892.5)))
            arguments=["g3a_execute.py","--freeze-commit","synthetic-freeze","--raw",str(root/"raw"),"--output",str(root/"output")]
            with patch.object(self.execute,"ROOT",root), patch.object(self.execute,"CONFIG",config), \
                    patch.object(self.execute,"SOURCES",[]), patch.object(sys,"argv",arguments), \
                    patch.object(self.execute,"subprocess",SimpleNamespace(run=lambda *a,**k:SimpleNamespace(returncode=0),
                                                                         check_output=lambda *a,**k:"synthetic-freeze")), \
                    patch.object(self.execute,"acquire_star",side_effect=acquisition.ScopeViolation("synthetic out-of-window row")) as acquire, \
                    patch.object(self.execute,"qualification") as qualify, redirect_stdout(io.StringIO()):
                with self.assertRaises(acquisition.ScopeViolation):
                    self.execute.main()
                self.assertEqual(acquire.call_count,1)
                qualify.assert_not_called()
            receipt=json.loads((root/"output/receipt.json").read_text())
            summary=json.loads((root/"output/summary.json").read_text())
            self.assertEqual(receipt["status"],"access_guard_stopped")
            self.assertEqual(len(summary["stars"]),1)
            self.assertFalse((root/"output/qualified-set.json").exists())


if __name__ == "__main__":
    unittest.main()
