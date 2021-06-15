# Python wrapper for the Misty API

(another) unofficial python wrapper for the Misty REST and WebSockets API, with text-to-speech

documentation: https://is-bibih.github.io/misty-py-wrapper/

## how to update documentation

Set `PYTHONPATH` environment variable to include the `misty-py-wrapper/misty-py-wrapper`
directory.

From `misty-py-wrapper`, generate documentation in dummy directory `new-docs`:
```
pdoc --html -f -o new-docs misty-py-wrapper
```

(Check generated documentation with internet browser.)

Move documentation to its correct directory and delete dummy folder.
```
mv new-docs/* docs
rm -r new-docs
```

Commit and push changes.

