import cloudinary
from pusher_push_notifications import PushNotifications
beams_client = PushNotifications(
    instance_id='89d4cf96-b227-4ce3-89d7-1203777ccc47',
    secret_key='7E6CDFBF03091A11715A0B17F2E572648EF4ED9E48B1A8887285CA66160D0E01',
)
cloudinary.config(
  cloud_name = "hhpni8wqv",
  api_key = "771619568363457",
  api_secret = "1JDNVnXB4zFcV4wVOH0e4s8y3Po"
)