from ..mongo.utils import MongoUtils
from pymongo import DESCENDING

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
            RiskIntegration.getAggregateSeverityScore(userId)
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
        
    def getAggregateSeverityScore(userId, k=10) -> float:
    # userViolations = MongoUtils.queryDocuments("violations", {"user_id": userId, "date": {"$gt": startDate}})
        db = MongoUtils.client["knacktohack"]
        violations = db["violations"]
        userViolations = violations.find({"user_id": userId}).sort("date", DESCENDING).limit(k)
        userViolations = [ele for ele in userViolations]
        
        aggScore = 0.0

        for ele in userViolations:
            aggScore += ele["score"]*float(ele["violation_priority"])

        aggScore = aggScore/len(userViolations)
        res = MongoUtils.updateUserDocument("users", {"user_id": userId}, {"severity_score": aggScore})
        print(res)
        return aggScore
