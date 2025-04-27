from setuptools import setup, find_packages

setup(
    name="damai-ticket",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "kivy==2.2.1",
        "requests==2.31.0",
        "pyyaml==6.0.1",
        "pillow==9.5.0",
        "certifi==2023.7.22",
        "charset-normalizer==3.3.2",
        "idna==3.6",
        "urllib3==2.0.7"
    ],
    author="DamaiTicket",
    author_email="support@example.com",
    description="大麦网自动抢票助手",
    keywords="damai, ticket, automation",
    python_requires=">=3.8",
) 