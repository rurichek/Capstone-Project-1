// set the dimensions and margins of the graph
const margin = {
  top: 60,
  right: 120,
  bottom: 160,
  left: 80
}

let width = 900 - margin.left - margin.right;
let height = 500 - margin.top - margin.bottom;

//will hold all the data from the .tsv file
let teamsArr = [];
let teamsObj = {};
let playerArr = [];

let optionHtml = '';
let optionArr = [];

let chartId;

let teamName = '';
let area = '';
let season = '';

let totalTeamWins;
let totalTeamLoss;
let totalTeamPlays;
let teamWinPercent;
let teamLossPercent;
let tooltip;

let yMax;
let xScale;
let yScale;
let zScale;

let keys;

let g;

/******************FUNCTIONS*********************/
const newTeamId = chartId => {
  playerArr = teamsObj[chartId];

  teamName = playerArr[0]['Team Name'];
  area = playerArr[0]['Area'];
  season = playerArr[0]['Season'];

  totalTeamWins = playerArr.reduce((acc, el) => acc + Number(el.Won), 0);
  totalTeamLoss = playerArr.reduce((acc, el) => acc + Number(el.Lost), 0);
  totalTeamPlays = totalTeamWins + totalTeamLoss;
  teamWinPercent = Math.round(totalTeamWins / totalTeamPlays * 100);
  teamLossPercent = Math.round(totalTeamLoss / totalTeamPlays * 100);

  //this converts some of the '-' fields to '0'
  playerArr.map(el => {
    if (el.Defaults === '-') {
      el.Defaults = '0';
    }
    if (el['Win %'] !== '-') {
      el['Win %'] = parseInt(el['Win %']);
    }
    if (el.Doubles === '-') {
      el.Doubles = '0';
    }
    if (el.Singles === '-') {
      el.Singles = '0';
    }
    return el;
  });

  tooltip = d3.select('body')
    .append('div')
    .classed('tooltip', true)
    .style('opacity',0);

  //array of all the keys in the player array (e.g., Player, City, etc)
  keys = teamsArr.columns.slice(1);

  d3.select('.svgChart')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .classed('svgClass', true);

  g = d3.select('.svgChart')
    .append('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`);

  //ON FIRST LOAD CALL REMOVE CHART
  //TO first remove any previous chart & draw new one
  removeChart('Matches');
};

const drawChart = type => {

  let colorArr = [];
  let keysArr = [];
  let chartTitle = '# ';

  //type is based on the select values (event listener)
  if (type === 'Matches') {
    colorArr = ['#A8927B', '#564036', '#EF7D5A'];
    //Default, Loss, Win
    keysArr = [keys[8], keys[17], keys[16]];
    chartTitle += 'Matches Won / Lost (by Player)';
  } else if (type === 'Won') {
    colorArr = ['#EF7D5A'];
    keysArr = [keys[16]];
    chartTitle += 'Matches Won (by Player)';
  } else if (type === 'Lost') {
    colorArr = ['#564036'];
    keysArr = [keys[17]];
    chartTitle += 'Matches Lost (by Player)';
  } else if (type === 'Singles') {
    colorArr = ['#516EBA'];
    keysArr = [keys[10]];
    chartTitle += 'Singles Matches Played (by Player)';
  } else if (type === 'Doubles') {
    colorArr = ['#E3C247'];
    keysArr = [keys[11]];
    chartTitle += 'Doubles Matches Played (by Player)';
  } else if (type === 'SinglesDoubles') {
    colorArr = ['#516EBA', '#E3C247'];
    keysArr = [keys[10], keys[11]];
    chartTitle += 'Singles / Doubles Matches Played (by Player)';
  } else if (type === 'WinPercentage') {
    colorArr = ['#EF7D5A'];
    keysArr = [keys[9]];
    chartTitle = 'Match Win Percentage (by Player)';
  }

  chartTitle += '*';

  drawTitle(chartTitle);
      //DRAW TEAM NAME
  drawTeamName();
  drawChartFooter();

  //sort by y-axis value (and if same values, then sort by last name alphabetically)
  if (type === 'SinglesDoubles') {
    playerArr.sort(function(a,b) {
      return Number(a.Matches) - Number(b.Matches) ||
        a.Player.localeCompare(b.Player);
    });
    yMax = d3.max(playerArr.map(d => {
      str_data = d['Matches'];
      num_data = Number(d['Matches']);
      return num_data;
    }));
  } else if (type === 'WinPercentage') {
    playerArr.sort(function(a,b) {
      return a['Win %'] - b['Win %'] ||
        a.Player.localeCompare(b.Player);
    });
    yMax = 100;
  } else {
    playerArr.sort(function(a,b) {
      return Number(a[type]) - Number(b[type]) ||
        a.Player.localeCompare(b.Player);
    });
    yMax = d3.max(playerArr.map(d => {
      str_data = d[type];
      num_data = Number(d[type]);
      return num_data;
    }));
  }

  xScale = d3.scaleBand()
    .rangeRound([0, width])
    .paddingInner(0.2)
    .align(0.1);
  xScale.domain(playerArr.map(d => d.Player));

  yScale = d3.scaleLinear()
    .rangeRound([height, 0])
    .domain([0, yMax]);

  zScale = d3.scaleOrdinal()
    .range(colorArr);

  g.append('g')
    .attr('class', 'chart')
    .selectAll('g')
    .data(d3.stack().keys(keysArr)(playerArr))
    .enter()
    .append('g')
      .attr('fill', d => zScale(d.key))
    .selectAll('rect')
    .data(d => d)
    .enter()
    .append('rect')
      .style('opacity', 0)
      .attr('class', 'bar')
      .attr('x', d => xScale(d.data.Player))
      .attr('y', d => yScale(d[1]))
      .attr('height', d => yScale(d[0]) - yScale(d[1]))
      .attr('width', xScale.bandwidth())
    .on('mouseenter', d => drawTooltipText(d))
    .on('mouseout', () => tooltip.style('opacity', 0));

  /*add transition effects to fade in*/
  g.selectAll('rect')
    .transition()
    .duration(800)
    .ease(d3.easeLinear)
    .style('opacity', 1);

  //call to functions
  drawLegend(keysArr);
  drawXAxis();
  drawYAxis();
};

const drawLegend = keys => {
  let legend = g
    .append('g')
      .attr('class', 'legend')
      .attr('font-family', 'sans-serif')
      .attr('font-size', 10)
      .attr('text-anchor', 'end')
    .selectAll('g')
    .data(keys.slice().reverse())
    .enter()
    .append('g')
      .attr('transform', (d, i) => `translate(0, ${i * 20})`);

  legend.append('rect')
    .attr('x', width + 85)
    .attr('width', 19)
    .attr('height', 19)
    .attr('fill', zScale);

  legend.append('text')
    .attr('x', width + 80)
    .attr('y', 9.5)
    .attr('dy', '0.32em')
    .text(d => d);
};

const drawTooltipText = d => {
  tooltip.html(`
    ${d.data.Player}<br>
    ${d.data['Win %']}% Win<br>
    Won: ${d.data.Won}; Lost: ${d.data.Lost}<br>
    ${d.data.Singles} Singles Played<br>
    ${d.data.Doubles} Doubles Played<br>
    City: ${d.data.City}<br>
    Rating: ${d.data.Rating}`
  )
  .style('opacity', 1)
  .style('left', d3.event.pageX + 'px')
  .style('top', d3.event.pageY + 'px');
};

const drawTeamName = () => {
  //first remove old team name
  d3.select('.teamName')
    .remove();
  //then draw the new team name
  d3.select('.svgChart')
    .append('text')
      .attr('class', 'teamName')
      .attr('x', (width + margin.left + margin.right) / 2)
      .attr('y', margin.top / 2)
      .attr('text-anchor', 'middle')
      .text(teamName);
};

const drawChartFooter = () => {
  //first remove old footer
  d3.select('.chartFooter')
    .remove();
  //then draw the new one
  d3.select('.svgChart')
    .append('text')
      .attr('class', 'chartFooter')
      .attr('x', margin.left + 10)
      .attr('y', height + margin.top + margin.bottom - 5)
      .attr('text-anchor', 'middle')
      .text('*Data from USTA NorCal');
};

const drawTitle = title => {
  //first remove old title
  d3.select('.chartTitle')
    .remove();
  //then draw the new chart title
  d3.select('.svgChart')
    .append('text')
      .attr('class', 'chartTitle')
      .attr('x', (width + margin.left + margin.right) / 2)
      .attr('y', margin.top - 5)
      .attr('text-anchor', 'middle')
      .text(title);
}

const drawXAxis = () => {
  let xAxis = d3.axisBottom(xScale);
  //add the x Axis
  d3.select('.svgChart')
    .append('g')
      .attr('class', 'xAxis')
      .attr('transform', `translate(${margin.left},`
        + `${height + margin.top})`)
      .call(xAxis)
    .selectAll('text')
      //ensures end of label is attached to the axis tick
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '-.15em')
      .attr('transform', 'rotate(-50)');
};

const drawYAxis = () => {
  let numTicks = yMax;
  if (yMax === 100) {
    numTicks = 10;
  }
  let yAxis = d3.axisRight(yScale)
    .ticks(numTicks);
  //add the y Axis
  d3.select('.svgChart')
    .append('g')
      .attr('class', 'yAxis')
      .attr('transform', `translate(${width + margin.left}`
        + `,${margin.top})`) //shifts axis
      .call(yAxis);
};

const removeChart = newVal => {
  let svg = d3.select('.svgChart');

  svg.select('.chart')
    .style('opacity', 1)
    /*add transition effects to fade out*/
    .transition()
      .duration(300)
      .ease(d3.easeLinear)
      .style('opacity', 0)
    .remove();
    setTimeout(() => {
      removeAxes();
      removeLegend();
      drawChart(newVal)
    }, 300);
};

const removeAxes = () => {
  d3.select('.svgChart')
    .select('.xAxis')
    .remove();
  d3.select('.svgChart')
    .select('.yAxis')
    .remove();
};

const removeLegend = () => {
  d3.select('.svgChart')
    .select('.legend')
    .remove();
};

/******************D3*********************/
d3.tsv('./player_data.tsv', file => {

  teamsArr = file;

  teamsObj = teamsArr.reduce((acc, el) => {
    let currTeamId = el['Team ID'];
    if (acc[currTeamId] === undefined) {
      acc[currTeamId] = [el];
    } else {
      acc[currTeamId].push(el);
    }
    return acc;
  }, {});

  for (let prop in teamsObj) {
    let currTeamName = teamsObj[prop][0]['Team Name'];
    optionArr.push([currTeamName, prop]);
  }

  //sort teams alphabetically
  optionArr.sort((a,b) => (a[0] < b[0]) ? -1 : 1);

  for (let i = 0; i < optionArr.length; i++) {
    //for each unique team, add id & team name
    //into option tags for select
    optionHtml += `
      <option value='${optionArr[i][1]}'>
      ${optionArr[i][0]}</option>
    `;
  }

  d3.select('#selectTeams')
    .html(optionHtml);

  d3.select('#selectTeams')
    .classed('hidden', false);
  d3.select('#selectTeamsLabel')
    .classed('hidden', false);

  newTeamId(optionArr[0][1]);


  /******************EVENT LISTENERS*********************/
  //when change select dropdown option
  //initiate a new team to draw the chart
  d3.select('#selectTeams').on('change', () => {
    let optionVal = d3.select('#selectTeams').property('value');
    newTeamId(optionVal);
  });

  //draw different charts based on which button is clicked
  d3.selectAll('.btnCustom').on('click', () => {
    d3.selectAll('.btnCustom')
      .classed('active', false);
    d3.event.preventDefault();
    d3.select(event.currentTarget)
      .classed('active', true);
    let newVal = d3.select(event.currentTarget).attr('data-val');
    removeChart(newVal);
  });
});
