# RedditCommenter

A simple Selenium-based Reddit comment poster that builds on the previous project "RedditCrawler".

An attempt was previously made to update posts from a list of target accounts with a list of upvoting accounts.

User agent randomization and Tor proxy are among the attempts made, but Reddit doesn't register them, because it probably detects the common source as suspicious/coming from the same person.

Now, we are able to work with GoLogin, an application that allows users to pay to have 2 or more cloud-hosted dedicated browser profiles with dedicated proxies. This bypasses Reddit's bot detection and successfully posts comments.

The script looks for login information in a Google Sheet, then uses the Gologin API to launch the profiles and Selenium to control the browser.

Windows only.

## Usage
Refer to "installation.txt" (all in french)