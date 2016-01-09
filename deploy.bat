del dist\*
python setup.py py2exe
copy kradfile-u dist
copy kanjidic dist
copy cedict_ts.u8 dist
copy edict2u dist
copy enamdict.utf dist
copy radicals dist
cd dist
ren gui.exe kanjiLookup.exe
cd ..

