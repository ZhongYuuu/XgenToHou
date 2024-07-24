import mtoa.ui.ae.templates as templates
from mtoa.ui.ae.templates import ShapeTranslatorTemplate, registerTranslatorUI

class xgmSplineDescriptionTemplate(ShapeTranslatorTemplate):
    def setup(self):
        self.commonShapeAttributes()
        self.addSeparator()

        self.addControl("aiMinPixelWidth")
        self.addControl("aiMode")

templates.registerTranslatorUI(xgmSplineDescriptionTemplate, "xgmSplineDescription", "xgenSplineTranslator")
