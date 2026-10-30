import yaml

def test_every_global_example_is_sourced_and_labelled():
    ex = yaml.safe_load(open("docs/global_examples.yaml", encoding="utf-8"))["examples"]
    gaps = {g["id"] for g in yaml.safe_load(open("docs/gap_register.yaml", encoding="utf-8")) if isinstance(g, dict) and "id" in g} \
        if isinstance(yaml.safe_load(open("docs/gap_register.yaml", encoding="utf-8")), list) else None
    for e in ex:
        assert e["status"] in ("verified_official", "verify_before_use", "not_found_in_jurisdictions_examined")
        assert e["url"].startswith("https://") or e["status"] == "not_found_in_jurisdictions_examined"
        if gaps is not None:
            assert e["gap"] in gaps
