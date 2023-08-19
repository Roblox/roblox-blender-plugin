# ROBLOX BLENDER PLUGIN
A Blender plugin to upload selected assets in Blender to Roblox using Roblox's Open Cloud API.

This project is licensed under the terms of the MIT license. See [LICENSE.md](https://github.com/Roblox/roblox-blender-plugin/blob/main/LICENSE.md) for details.

**Roblox is providing this plugin source as a reference implementation, and we encourage the community to extend and build upon this!**

https://github.com/Roblox/roblox-blender-plugin/assets/66378309/4e889d87-c0fc-4af5-b974-9eb129d16364


# INSTALLATION
## UNINSTALL OLD VERSION
1. Navigate to the add-ons menu in Blender at `Edit` > `Preferences` > `Add-ons`
2. In the top-right search window, search for `Roblox`
3. If `Upload to Roblox` is present, click the left arrow to expand it and click `Remove` to uninstall it
4. Restart Blender after uninstalling

## INSTALL NEW VERSION
1. Be sure to [uninstall any old version](#uninstall-old-version) first, including restarting Blender afterward
2. Download the latest add-on zip file from the [repository releases page](https://github.com/Roblox/roblox-blender-plugin/releases)
3. Navigate to the add-ons menu in Blender at `Edit` > `Preferences` > `Add-ons`
4. Click `Install`
5. Select the **zip file** downloaded above and click `Install Add-on` _(Do not unzip the file!)_
6. In the top-right search window, search for `Roblox`
7. Find the `Import-Export: Upload to Roblox` add-on in the list, and ensure the checkbox next to its name is checked
8. Open the plugin's main panel by going to a 3D window, pressing `N`, and selecting the `Roblox` tab
9. Click `Install Dependencies`. This is only required the first time the plugin runs
10. Once it says `Installation complete!`, *restart Blender*
11. The plugin is now ready for use

# USAGE GUIDE
## LOG IN
1. Be sure to complete the [installation steps](#install-new-version), including dependency installation and restarting Blender
2. Open the plugin's main panel by going to a 3D window, pressing `N`, and selecting the `Roblox` tab
3. Click `Log in`
4. Unless previously logged in, your browser opens and prompts for authorization
5. In your browser, authorize creators to use in the plugin. To do this, log into your Roblox account. Then, select the account and/or groups you want to upload with. Click `CONTINUE` at the bottom of the page, then click `CONFIRM AND GIVE ACCESS`. Your browser should indicate a successful login. You can close the page and return to Blender
6. Select the desired creator from the `Upload to:` dropdown of authorized creators
## UPLOAD
1. Select any number of meshes or collections you want to publish at once. Each selected object will be uploaded as its own asset. If you want to publish multiple objects as a single asset, group them into a `Collection` and select the `Collection`
2. Click `Upload`
3. Open Roblox Studio and search for your object under `Home` > `Toolbox` > `Inventory` (tab) > `My Packages` (dropdown) _This list is currently unordered, you can use `Search` to find it by the name matching the object name in Blender_

## ASSET VERSIONING & AUTO-UPDATING CHANGES
Since objects are uploaded as packages, we can take advantage of package behavior to automatically pull in changes
when you publish a new version of the package.
1. In Roblox Studio, after inserting the package into your hierarchy, select the `PackageLink` object inside the package
2. Ensure the `AutoUpdate` property of the `PackageLink` is checked
3. When a new version of this object is uploaded from Blender, this package will automatically update to the latest version, overwriting any modifications
4. This package association is tracked in Blender under the `Custom Properties` of an object or collection, where it stores the `Roblox Package ID`
5. **To upload a previously-published asset to a new asset ID instead of uploading as a new version,** delete this `Roblox Package ID` custom property
# CONTRIBUTING
Roblox is providing this plugin source as a *reference* implementation. Our goal is to illustrate how Open Cloud APIs can be used to create integrations with external tools.

Our hope is the community leverages this reference implementation to build their own tools and extensions. We actively encourage anybody who wishes to extend this reference implementation with new features to fork this repository and share their work with the community.

As such, we will *not* be accepting Pull Requests that introduce new features or functionality. However, in the interests of ensuring this plugin remains a functional reference implementation, we will be accepting Pull Requests for bug fixes.


## RUNNING FROM SOURCE CODE
Do either of the following options to install the plugin:

### OPTION 1: RECOMMENDED VS CODE DEVELOPMENT WORKFLOW
This option allows you to quickly iterate on the codebase and reload the plugin for testing changes, as well as use a
debugger during development.

1. Be sure to [uninstall any plugin zip file](#uninstall-old-version) first, and then close Blender
1. Open VS Code as administrator to allow the Blender Development plugin to install a debugger for Blender _(Only need to do this the first time)_
2. Install the VS Code extension [JacquesLucke.blender-development](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development)
3. Open the repository in VS Code
4. Open the command window (`ctrl`/`⌘` + `shift` + `p`)
5. Run the `> Blender: Build and Start` command 
6. Select your Blender executable file
7. The plugin is now running in Blender with a debugger attached
8. If saving a file does not auto-reload the plugin, you can manually reload the plugin with `> Blender: Reload Addons`

### OPTION 2: INSTALL MANUALLY

1. Zip the top-level repository folder such that the first level inside the zipped folder is another single folder containing everything
2. Follow the steps to [install a new version](#install-new-version) using this zipped folder instead of the one from the releases page

## PULL REQUESTS
Before marking your pull request as ready for review, please ensure:

- Your pull request does not introduce new features or functionality
- All python files are formatted with [black](https://pypi.org/project/black/) and the CI format check is passing
- Any dependency changes are reflected in `requirements.txt`
- All commit messages are complete and informative
- Your Pull Request includes a description of the bug and how your changes fix the bug

## CONTINUOUS INTEGRATION CHECKS
Github Actions is set to check that formatting matches [black formatting](https://black.readthedocs.io/en/stable/index.html) before allowing a merge to `main`. Be sure to format your python code with `black` before pushing to avoid being blocked. You can use the VS Code plugin [Black Formatter by Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter), or run the command line tool by installing it via `pip install black` and then running `black .`

## CREATING A RELEASE
Releases are set up to automatically generate via Github Actions when a tag is added to a commit with the format `v[0-9]+.[0-9]+.[0-9]+`. For example, you can create a release from a commit with SHA `a1b2c3d` by doing the following:

> `git tag -a v0.0.0 a1b2c3d -m "My message for v0.0.0"`

Or, tag the latest commit with:

> `git tag -a v0.0.0 HEAD -m "My message for v0.0.0"`

- where `v0.0.0` represents a [semantic versioning](https://semver.org/) naming scheme `v[major].[minor].[patch]`
- where `[major]` gets bumped for non-backward compatible changes,
- where `[minor]` gets bumped for backward-compatible features,
- and where `[patch]` gets bumped for backward-compatible fixes.

Once you've created your tag, push it to the repository with
> `git push --tags`

## PLUGIN VERSIONING
The plugin version is automatically updated by a Github Actions workflow to correspond with the committed version tag name (as described in [Creating a Release](#creating-a-release)).
The version doesn't get committed to the codebase, so if you run the plugin locally instead of using a release, your plugin will just show the default version number that exists in the codebase.
