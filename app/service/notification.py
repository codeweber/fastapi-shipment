
import asyncio

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from app.service.utils import TEMPLATES_DIR

from ..settings import notification_settings

class NotificationService:
    def __init__(self, background_tasks: BackgroundTasks):
        self.fastmail = FastMail(
            ConnectionConfig(
                **notification_settings.model_dump(),
                TEMPLATE_FOLDER=TEMPLATES_DIR
            )
        )
        self.tasks = background_tasks

    def _send_email_sync(
        self,
        recipients: list[EmailStr],
        subject: str,
        body: str    
    ) -> None:
        asyncio.run(
            self.fastmail.send_message(
                message=MessageSchema(
                    recipients=recipients,
                    subject=subject,
                    body=body,
                    subtype=MessageType.plain
                )
            )
        )

    def send_email(
        self,
        recipients: list[EmailStr],
        subject: str,
        body: str
    ) -> None:
        
        # Following code takes ~3s to execute
        # self.tasks.add_task(
        #     self.fastmail.send_message,
        #     message=MessageSchema(
        #             recipients=recipients,
        #             subject=subject,
        #             body=body,
        #             subtype=MessageType.plain
        #         )
        # )
        
        # Following code tasks ~25ms to execute
        # Apprarently wrapping the "async" in a sync task works, as fastapi runs this in a separate thread
        # Find for learning; but this would need to be resolved for a production deployment
        # Note a similar issue here: 
        self.tasks.add_task(
            self._send_email_sync,
            recipients=recipients,
            subject=subject,
            body=body
        )

    def _send_email_with_template_sync(
        self,
        recipients: list[EmailStr],
        subject: str,
        template_body: dict,
        template_name: str,
    ) -> None:
        asyncio.run(
            self.fastmail.send_message(
                message=MessageSchema(
                    recipients=recipients,
                    subject=subject,
                    template_body=template_body,
                    subtype=MessageType.html
                ),
                template_name=template_name
            )
        )


    def send_email_with_template(
        self,
        recipients: list[EmailStr],
        subject: str,
        template_body: dict,
        template_name: str,
    ) -> None:
        
        self.tasks.add_task(
            self._send_email_with_template_sync,
            recipients=recipients,
            subject=subject,
            template_body=template_body,
            template_name=template_name
        )