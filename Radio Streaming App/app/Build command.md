**For Windows:**



*pyinstaller --onedir --icon=icon.ico --noconsole --add-data "files;files" --add-data "ffplay;ffplay" radio.py*



Delete 'build' and 'dist' folders and radio.spec before running



**For Linux:** 



*pyinstaller --onedir --icon=icon.ico --noconsole --add-data "files:files" --add-data "ffplay:ffplay" radio.py*



Delete 'build' and 'dist' folders and radio.spec before running



You must compress and extract the files on Linux, as Windows (and apps) cannot do anything with Linux binaries

