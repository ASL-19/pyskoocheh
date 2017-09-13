# Paskoocheh Library

Pyskoocheh aws integration api module

Facilitates integration with SES, S3 and DynamoDB for
paskoocheh-related activities.

## Usage
### pyskoocheh.actionlog
#### Functions

    is_limit_exceeded(user_name, action_name, expiry=86400)
    user_has_requested_file(user_name)
    log_action(user_name, action_name, source)
    clean_action_log(age)

### pyskoocheh.feedback
#### Functions

    get_feedback_digest(table_name, days=1)
    send_email(email_from, email_to, subject, text_body, html_body, file_name, file_data)
    send_feedback(table_name, user_name, subject, message)
    template_email_link(text_body, html_body, attachment_html, link)

### pyskoocheh.storage
#### Functions

    build_key_name(app_name, os_name, file_name)
    build_static_link(bucket, key)
    get_binary_contents(bucket, key)
    get_json_contents(bucket, key)
    get_object_metadata(bucket, key)
    put_object_metadata(bucket, key, meta_key, meta_value)
    get_temp_link(bucket, key, key_id, secret_key, expiry=300)
    put_doc_file(bucket, key, filename, url, caption=None, thumb=None)
    put_text_file(bucket, key, text)
    add_to_mailing_list(user_email)

### pyskoocheh.telegram
#### Functions

    get_file_path(token, file_id)
    hide_keyboard(token, chat_id, text)
    make_file_url(token, file_path)
    make_getfile_url(token)
    make_keyboard(items, items_per_row=0, add_home=True)
    send_file(token, chat_id, text, file_link, keyboard=None)
    send_keyboard(token, chat_id, text, keyboard, one_time=True, resize=True)
    send_message(token, chat_id, text, keyboard=True)
    save_request(chat_id, msg_id, user_name, event, table_name="MajlisMonitorBot")

### pyskoocheh.crypto

Provides PGP-based crypto functions 

#### Classes
##### SignatureManager

     Compute the pgp signature and sha256 checksum of the binary content of posted files to the backend or a text strings.
     calc_signature
     sign_string
     calc_compute_checksum

### pyskoocheh.google_play_store
#### Functions

##### DEPENDENCIES:
  * Python 2.7+
  * Python Modules:
    * requests
    * PyCrypto

##### MOTIVATION:
  * Google has updated its server side authentication regarding the Google Play Store API, consequently breaking authentication with E-mail and Password combination in unofficial Python Google Play Store API modules (August 2017).
  * Token authentication was still functional, however there existed only a Java Google Play Store Token Dispenser.
  * Translating the Java Google Play Store Token Dispensers to Python provided many benefits to our projects that need Google Play Store authentication.
  * Original Java sources:
    * https://github.com/yeriomin/token-dispenser
    * https://github.com/yeriomin/play-store-api

##### OBJECTIVE:
  * Provided the correct E-mail and Password credential combination, returns a Google Play Store Authentication Token which can then be used with the Google Play API

##### USAGE:
  * As a standalone application:
    * `$ python google_play_store.py <e-mail> <password>`
  * As a Python module:
    * Import the module in your Python application `import google_play_store as gpstd`
    * Request for token: `gpstd.GooglePlayStoreTokenDispenser("<e-mail>", "<password>").get_token()`
    * Or

```
        gpstd.GooglePlayStoreTokenDispenser()           \
             .set_credentials("<e-mail>", "<password>") \
             .get_token()
```
