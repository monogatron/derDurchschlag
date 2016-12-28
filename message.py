



class Message: 
    
    def __init__(self, in_path, in_date, in_time, in_fromNumber, in_positionInMultiMessage, in_content, in_isPullMessageRequest, in_answerIndex):
        self.path = in_path
        self.date = in_date
        self.time = in_time
        self.fromNumber = in_fromNumber
        self.positionInMultiMessage = in_positionInMultiMessage
        self.content = in_content
        self.isPullMessageRequest = in_isPullMessageRequest
        self.answerIndex = in_answerIndex                   #which answer is the right one for the pullMessageRequest?


    
