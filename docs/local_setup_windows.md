# Local Setup on Windows

These notes describe a user-level Windows setup for OpenTrialDQ.

## Python

Install Python for your user account and verify it from a new Command Prompt:

```cmd
python --version
python -m pip --version
```

Install OpenTrialDQ in editable mode:

```cmd
cd C:\Users\akhila.chanubala\Documents\GitHub\OpenTrialDQ
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Java for PySpark

PySpark requires Java. If Java is installed through Eclipse Temurin for your user account, set `JAVA_HOME` before running tests:

```cmd
set JAVA_HOME=C:\Users\akhila.chanubala\AppData\Local\Programs\Eclipse Adoptium\jdk-17.0.19.10-hotspot
set PATH=%JAVA_HOME%\bin;%PATH%
java -version
```

## Run Tests

```cmd
cd C:\Users\akhila.chanubala\Documents\GitHub\OpenTrialDQ
python -m pytest
```

Expected result:

```text
1 passed
```
