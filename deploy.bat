rem python setup.py py2exe
pyinstaller -w gui.pyw
copy kradfile-u dist\gui
copy kanjidic dist\gui
copy cedict_ts.u8 dist\gui
copy edict2u dist\gui
copy enamdict.utf dist\gui
copy radicals dist\gui
cd dist
cd gui
ren gui.exe kanjiLookup.exe
cd ..
cd ..
