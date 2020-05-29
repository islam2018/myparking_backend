import cloudinary
from pusher_push_notifications import PushNotifications
import pusher
beams_agent_client = PushNotifications(
    instance_id='89d4cf96-b227-4ce3-89d7-1203777ccc47',
    secret_key='7E6CDFBF03091A11715A0B17F2E572648EF4ED9E48B1A8887285CA66160D0E01',
)
beams_driver_client = PushNotifications(
    instance_id='68987f6c-1b73-4e06-8515-b8db77033090',
    secret_key='BB3232FF32F5C90134AC13A975246478FC54424C91C6B459D938250030A9DCA0',
)
pusher_client = pusher.Pusher(
  app_id="1008479",
  key="64aeb36b21ab17679882",
  secret="1dfcaba05e0e0bf38ec6",
  cluster="eu"
)
cloudinary.config(
  cloud_name = "hhpni8wqv",
  api_key = "771619568363457",
  api_secret = "1JDNVnXB4zFcV4wVOH0e4s8y3Po"
)