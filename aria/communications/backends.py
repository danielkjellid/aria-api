import email
import logging
import os
import sys
import uuid
from typing import Any, Sequence

from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class BrowserEmailBackend(BaseEmailBackend):
    """
    Email backend used during development. The backend
    automatically opens an email in the browser instead
    of sending it.
    """

    @staticmethod
    def partition_multipart_email_payload(payload: Any) -> str:
        """
        Partition payload as the actual content starts after mime type headers
        and two newlines.
        """
        payload_as_str = str(payload)
        return payload_as_str.partition("\n\n")[2]

    @staticmethod
    def open_email_page(html: str) -> None:
        """
        Writes the provided html to a temporary file and opens it in
        the browser.
        """

        filename = f"/tmp/{uuid.uuid4()}.html"

        with open(filename, "w", encoding="utf-8") as file:
            file.write(html)

        # Open is default for darwin systems, linux uses xdg-open.
        open_cmd = "xdg-open" if sys.platform in ("linux", "linux2") else "open"

        logger.info("Wrote browser email to %s", filename)
        os.system(f"{open_cmd} {filename}")

    @staticmethod
    def _html_text_body_base(text: str) -> str:
        """
        Utility for the text part of emails. Creates a simple html page with
        pre tags to display text content.
        """

        return f"""
        <html>
            <head>
            </head>
            <body>
                <div style="margin-top: 50px;">
                    <pre>{text}</pre>
                </div>
            </body>
        </html>
        """

    def write_message(self, email_message: EmailMessage) -> None:
        """
        Extract email message data and write to file.
        """

        # Prepare message data for decoding.
        message = email_message.message()
        message_data = message.as_bytes()

        message_charset = (
            message.get_charset().get_output_charset()
            if message.get_charset()
            else "utf-8"
        )

        # Decode and extract message.
        message_data = message_data.decode(message_charset)
        email_msg = email.message_from_string(message_data)

        if email_msg.is_multipart():
            text_body = self.partition_multipart_email_payload(
                email_msg.get_payload()[0]
            )
            html = self._html_text_body_base(text_body)
            self.open_email_page(html)

            # The text part is the first part, the html part is the second.
            html_body = self.partition_multipart_email_payload(
                email_msg.get_payload()[1]
            )
            self.open_email_page(html_body)

            return

        text_body = str(email_msg.get_payload())
        html = self._html_text_body_base(text_body)
        self.open_email_page(html)

        return

    def send_messages(self, email_messages: Sequence[EmailMessage]) -> int:
        """
        Override send_message method of BaseEmailBackend.
        """

        if not email_messages:
            return 0

        for message in email_messages:
            self.write_message(message)

        return len(email_messages)
