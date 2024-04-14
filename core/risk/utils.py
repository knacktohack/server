from ..mongo.utils import MongoUtils

RISK_THRESHOLD = 0.82


class RiskIntegration:

    @staticmethod
    def isRisky(score):
        return score > RISK_THRESHOLD

    @staticmethod
    def persistRisk(
        userId, conversationId, questionName, score, organizationName="knacktohack"
    ):

        if RiskIntegration.isRisky(score):
            MongoUtils.insertViolation(
                userId, conversationId, questionName, score, organizationName
            )
            RiskIntegration.alertingService(userId, organizationName)
            return True

        return False

    @staticmethod
    def alertingService(userId, organizationName="knacktohack"):
        violationsOneDayBefore = (
            MongoUtils.queryViolationsByUserIdAndOrganizationNameAndDateBefore(
                userId, 1
            )
        )
        violationsOneWeekBefore = (
            MongoUtils.queryViolationsByUserIdAndOrganizationNameAndDateBefore(
                userId, 7
            )
        )
