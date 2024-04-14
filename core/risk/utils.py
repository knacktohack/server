from ..mongo.utils import MongoUtils

RISK_THRESHOLD = 0.82
DELTA = 0.03

class RiskIntegration:

    @staticmethod
    def isRisky(threshold,score):
        return  score > threshold

    @staticmethod
    def persistRisk(
        userId, conversationId, questionName, score, prompt,organizationName="knacktohack"
    ):
        threshold = MongoUtils.queryQuestionRiskThresholdByQuestionName(questionName)
        if RiskIntegration.isRisky(threshold,score):
            MongoUtils.insertViolation(
                userId, conversationId, questionName, score, organizationName
            )
            RiskIntegration.alertingService(userId, organizationName)
            return True

        if(threshold - score < DELTA):
            MongoUtils.insertPotentialViolation({
                "question_name": questionName,
                "score": score,
                "prompt": prompt
            })
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
