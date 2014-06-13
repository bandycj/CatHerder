# CatHerder

## Configure
Make a copy of config/sample.py and fill in the blanks.
These are the only oauth providers known to work with the oauth code:
   
    
### [Google](https://console.developers.google.com/project)
   1. Create a project, ID and name don't matter.
   2. Go to `APIs & Auth` -> `Credentials`.
   3. Click `Create new Client ID`.
   4. Click `Edit Settings` under the new ID.
   5. In the `Authorized redirect URI` text area enter `http://127.0.0.1/authorized/google`.

### [Facebook](https://developers.facebook.com/)
   1. Click `Apps` -> `Create a New App`, Display Name and Namespace don't matter.
   2. Go to `Apps` -> `<your app name>`.
   3. Click `Settings` and then the `Advanced` tab.
   4. Make sure all settings are set to `No` under the `App Restrictions` section.
   5. Make sure everything under `Security` blank.
   6. Set `Valid OAuth redirect URIs` to `http://127.0.0.1/authorized/google`.


#### Running
To run you need to define the CATHERDER_CONFIG environment variable to point at your config. That's it!
