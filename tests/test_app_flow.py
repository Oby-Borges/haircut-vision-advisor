from pathlib import Path

from streamlit.testing.v1 import AppTest

from haircut_vision.catalog import load_catalog

APP = Path(__file__).resolve().parents[1] / "app.py"


def click(app, label):
    next(b for b in app.button if b.label == label).click().run()
    assert not app.exception


def test_demo_to_approved_handoff_and_retake():
    app = AppTest.from_file(str(APP), default_timeout=20)
    app.query_params["demo"] = "1"
    app.run()
    assert not app.exception
    assert next(b for b in app.button if b.label == "Continue to preferences →").disabled
    click(app, "Load four-view demo")
    click(app, "Continue to preferences →")
    click(app, "Save preferences & find styles →")
    click(app, "Open Style studio →")
    images = app.get("image")
    assert len(images) == len(load_catalog()) + 5  # top 3, gallery, selected, preview
    captions = {item.caption for element in images for item in element.proto.imgs}
    assert {style.name for style in load_catalog()} <= captions
    assert any("Nano Banana 2" in caption.value for caption in app.caption)
    click(app, "Approve this style & preview")
    assert app.session_state.trim_session["plan"]["approved"]
    app.slider[0].set_value(1.1).run()
    assert app.session_state.trim_session["approval"] is None
    click(app, "Approve this style & preview")
    approved_id = app.session_state.trim_session["plan"]["plan_id"]
    app.radio(key="page").set_value("04  Integration").run()
    assert not app.exception
    assert any("One team" in m.value for m in app.markdown)
    assert any("Stage 1 — Networks" in m.value for m in app.markdown)
    app.radio(key="page").set_value("03  Style studio").run()
    assert app.session_state.trim_session["plan"]["plan_id"] == approved_id
    assert app.session_state.trim_session["approval"] is not None
    assert app.slider[0].value == 1.1
    app.radio(key="page").set_value("01  Capture").run()
    app.button(key="retake_rear").click().run()
    assert app.session_state.trim_session["plan"] is None
