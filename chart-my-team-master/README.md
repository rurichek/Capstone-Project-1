# Chart My Team

### A single-page web application that allows users to better access & visualize data about USTA NorCal tennis teams in the Bay Area. Built using D3 & Python, with data scraped from [www.ustanorcal.com](https://www.ustanorcal.com).

Note: this prototype was built using a sampling of USTA NorCal teams. Specifically, data was scraped for 1300+ players on 60+ Women's 4.0 (NTRP level) teams in the Bay Area (e.g., SF, East Bay, South Bay, and North Bay) for the 2016 Adult 18+ season [https://www.ustanorcal.com/listteams.asp?leagueid=1823](https://www.ustanorcal.com/listteams.asp?leagueid=1823). In the future, additional data can be added.

#### Screenshot of the app vs. original site:
On the USTA NorCal site, data about teams is displayed in a table format. (For example: [https://www.ustanorcal.com/teaminfo.asp?id=69321](https://www.ustanorcal.com/teaminfo.asp?id=69321)) This project converted this data into interactive bar charts that help users better visualize team data for players. 

##### Chart My Team:
![Image of Chart My Team](img/chartMyTeam.png?raw=true "Chart My Team")

##### Original Site (from which data was scraped)

![Image of USTA Norcal Site](img/ustaSite.png?raw=true "Original Data")

#### App Features Include:
* User can select from **60+ teams** (i.e., women's 4.0 teams in the Bay Area for the 2016 Adult 18+ season) and view data about a total of **1300+ players**.

* For each team, users can view **6 bar charts** visualizing data about # of matches played or win % (y-axis) by player (x-axis):
	* \# matches won & lost
	* \# matches won
	* \# matches lost
	* % of matches won
	* \# singles & doubles matches played
	* \# single matches played

* For each chart, the user can hover over a bar on the chart to see additional **tooltip data** summarizing the player:
	* Name
	* Win %
	* \# matches won/lost
	* \# singles & \# doubles matches played
	* City
	* NTRP Rating


#### Resources Used:

* USTA NorCal data: [https://www.ustanorcal.com](https://www.ustanorcal.com)

#### Technology Used:
* D3
* Python
* BeautifulSoup
* JavaScript
* Bootstrap
