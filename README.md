# Securing Flywheel API Keys

It is critical that we do not allow API keys for Flywheel to become
available to unauthorized users. 

API keys can be generated and re-generated from a user's Flywheel
profile. Anyone in possession of that key can perform actions as
that user. 

Regenerating the key invalidates the previous key. This process is
fast and can be done as often as needed, so if there is any question
of a key being exposed, it should be regenerated immediately. 

It's probably good practice to periodically regenerate
keys, as this will invalidate older keys and expose locations where
the old key was being used. 


# Uses of the API Key


## Command line interface calls

The `fw` [command line
interface](https://docs.flywheel.io/hc/en-us/articles/360008162214-Installing-the-Command-Line-Interface-CLI-)
(CLI) requires a user to authenticate with their key, for example

```
fw login university.flywheel.io:123456789abcde
```

These logins are persistent until explicitly undone with `fw logout`,
and will work for both the CLI and API. It works by creating a file
under the user's home directory - see below for details.


## API calls

In Python,

```
# import flywheel package
import flywheel

# Create client
fw = flywheel.Client('my-key')
```

The `Client()` method can also be called with no arguments,

```
# Create client
fw = flywheel.Client()
```

which requires a separate login. An alternative method is to call
`flywheel.Flywheel('my-key')`. Unlike `Client()`, this cannot be
called with no arguments.


# Preventing key exposure in code

## Require CLI login

Where possible, prefer `flywheel.Client()` to require the user to
login before running your code.


## Retrieve API keys with environment variables

An example function, which allows the user to either login from the
CLI ahead of time, or place the API key in the variable
`FLYWHEEL_API_KEY`:

```
import os

def flywheelClient():
  fw = None
  
  apiKey = os.environ.get('FLYWHEEL_API_KEY')
  
  # These calls will throw an exeption if a user is not logged in or
  # an invalid key is supplied 
  if apiKey is not None:
    fw = flywheel.Client(apiKey)
  else:
    fw = flywheel.Client()
  
  user = fw.get_current_user()
  
  print("Returning flywheel client for user %s %s (%s)\n" 
  % (user.firstname, user.lastname, user.id))
  
  return fw
```

Using an evironment variable makes it easier for users to put their
API key in their profile and avoid adding it to wrapper scripts that
they might themselves push to Github. 


## Separate source and runtime directories

It's good practice in general not to run things from within the source
directory, or place output files there. 

Some applications store history, autosaves, or other information
locally. For example, R will create `.Rhistory` in its working
directory. A script run in debug mode might echo the key to a log
file. 


# Git practices

General good practice will reduce the risk of leaks:

* Avoid wild cards with `git add`
* Run `git diff --cached` before committing to review changes


## Using the .gitignore

Github has published an extensive list of suggested files to
[ignore](https://github.com/github/gitignore) for different
languages. A `.gitignore` file can be placed in individual
repositories. Developers can additionally create a global ignore file,
and apply it with

```
git config --global core.excludesfile ~/.gitignore_global
```


# Preventing key exposure within the local environment

When a user authenticates to Flywheel, their key is stored as plain
text in this file

```
~/.config/flywheel/user.json
```

As far as I can tell, this file persists until a log out with

```
fw logout
```

This is how you can log in once on the CLI and then use that
credential in other terminal sessions or in the API. 

Any time you type your API key for an interactive login, via the CLI
or SDK, the key will likely be stored in a history file. Usually these
are stored in your home directory, for example

```
~/.bash_history
~/.python_history
```

These files should be readable by the user only, the easiest way to
accomplish this is to restrict permissions of the user's home
directory. 



# Detecting leaks on Github with truffleHog

[truffleHog](https://github.com/dxa4481/truffleHog) is an open source
tool that can be used to search commit histories for a variety of keys
including Flyhweel, AWS, and Google. 

By default it uses entropy checks to search for "key-like" objects,
but you can also define your own rules using regular expressions in a
JSON file:

```
{
  "Flywheel API Key": "upenn.flywheel.io:.*"
}
```

An example call: 

```
trufflehog --rules rules.json \
  --entropy FALSE \
  --regex \
  --rules rules.json \
  file:///path/to/a/repo
```

The repository URL can point to a locally cloned repo, as above, or to
a URL on Github. Using the above rules example, we only search for
Flywheel API keys, but you can add expressions to look for a [variety
of other
objects](https://github.com/dxa4481/truffleHogRegexes/blob/master/truffleHogRegexes/regexes.json). 

To search public repositories, see the script in `checkRepos.py`. The
curl commands can be modified to search private repositories by
providing the appropriate access token. See the [Github API developer
documentation](https://developer.github.com/v3/guides/getting-started/).



# Preventing leaks prospectively with git secrets

The AWS developers created [git
secrets](https://github.com/awslabs/git-secrets) to prevent AWS keys
being pushed to Github, but it is also extendable to look for other
keys. 

A nice feature of `git secrets` is that it supports easy installation
of git hooks, so that a repository owner can automatically scan for
prohibited text when a `git commit` is executed. It can also search
the commit history like `truffleHog`.

