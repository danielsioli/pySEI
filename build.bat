del /f dist\*
python setup.py sdist bdist_wheel
python -m twine upload dist/*
cd..
pause
pip install pySEI --upgrade