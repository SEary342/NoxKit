from noxkit.tools import BanditChecker, RuffChecker
from noxkit.tools.format import RuffFormat
from noxkit.tools.testing import PytestChecker, PytestCoverageChecker

tools = {
    "lint": (RuffChecker,),
    "format": (RuffFormat,),
    "scan": (BanditChecker,),
    "coverage": (PytestChecker, PytestCoverageChecker),
}
