
class Config:
    SECRET_KEY = '<set secret_key>'
    SQLALCHEMY_DATABASE_URI = 'postgresql://<set username>:' \
                                            '<set password>@localhost:5432/' \
                                            '<set database name>'
    
    # Zde jsou nastavení pro poštovní službu gmail,
    # ale pokud budete používat jiný poštovní server,
    # změňte všechny následující hodnoty podle nastavení vašeho serveru.

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = '<email>'
    
    # Pokud nevíte, jak nastavit app_password, klikněte na odkaz
    # https://support.google.com/mail/answer/185833?hl=en-GB
    
    MAIL_PASSWORD = '<app_password>'
    MAIL_DEFAULT_SENDER = 'noreply@demo.com'

