baseUrl = 'http://127.0.0.1:5433';
const urlParams = new URLSearchParams(window.location.search);
const journeyDate = urlParams.get('date');
const flightNumber = urlParams.get('flight');
const some_delay_message = "Unfortunately, your flight would be delayed. ";
const no_delay_message = "Congratulations, your flight is on time. You can look for additional insights below.";

function makeRequest(method, url, body) {
    return new Promise(function (resolve, reject) {
        var xhr = new XMLHttpRequest();
        xhr.open(method, url);
        xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
        xhr.onload = resolve;
        xhr.onerror = reject;
        xhr.send(body);
    });
}


function OnDashboardLoad(){
    var responseSingleFlightSeries;
    makeRequest('POST', baseUrl + '/predict/singleFlightSeries', JSON.stringify({ flightId: flightNumber, days: 10,
     date: journeyDate }))
        .then(function (e) {
            console.log(e.target.response);
            if(e.target.response == "[]"){
                confirm("Oh no! The flight and date combination you selected is not in our database. Please select other flight/date.");
                location.replace(baseUrl);
                return;
            }
            responseSingleFlightSeries = JSON.parse(e.target.response);
            
            // add preprocessing code and call to generate graph
            var timeConv = d3.timeParse("%Y-%m-%d");
            var lineSvg = LineChart(responseSingleFlightSeries,{
                x: d=>timeConv(d.date),
                y: d=>d.Prediction,
                yLabel: "↑ Flight Delay",
                width: 600,
                height: 500,
                color: "steelblue",
                marginLeft: 50,
                marginRight: 50,
            })
            d3.select("#line_chart").append(() => lineSvg)
           
            }).catch(function(error) {
            console.log(error);
        }, function (e) {
            // handle errors
        });
    
    var responseSingleFlightDelay;
    makeRequest('POST', baseUrl + '/predict/singleFlight', JSON.stringify({ flightId: flightNumber, date: journeyDate}))
        .then(function (e) {
            console.log(e.target.response);
            if(e.target.response == "[]"){
                confirm("Oh no! The flight and date combination you selected is not in our database. Please select other flight/date.");
                location.replace(baseUrl);
                return;
            }
            responseSingleFlightDelay = JSON.parse(e.target.response);
            // Flight details
            // display flight data
            document.getElementById("flightNumber").textContent = flightNumber
            document.getElementById("doj").textContent = journeyDate
            document.getElementById("origin").textContent = responseSingleFlightDelay.ORIGIN
            document.getElementById("destination").textContent = responseSingleFlightDelay.DESTINATION
            if(responseSingleFlightDelay.Prediction == "No Delay Predicted"){
                document.getElementById("delay_message").textContent = no_delay_message;
            }
            else{
                document.getElementById("delay_message").textContent = responseSingleFlightDelay.Prediction
            }
            //Add bar chart
            var barSvg = BarChart(responseSingleFlightDelay.MLI, {
                x: d => d.feature_names,
                y: d => Math.abs(+d.feature_importances),
                xDomain: d3.groupSort(responseSingleFlightDelay.MLI, ([d]) => -Math.abs(+d.feature_importances), d => d.feature_names), // sort by descending frequency
                yFormat: "%",
                width: 600,
                height: 500,
                yLabel: "↑ % Contribution",
                xLabel: "Factors",
                color: "steelblue",
                marginLeft: 50,
                marginRight: 50,
              })
            d3.select("#bar_chart").append(() => barSvg)
            //Add recommendations
            const table = document.querySelector('tbody')
            var city = responseSingleFlightDelay.Recommendations[0]["Origin City"] == undefined ? "Destination City" : "Origin City"
            document.getElementById("PlaceId").textContent = (city.split(' ')[0])
            responseSingleFlightDelay.Recommendations.forEach((item) => {
                table.innerHTML = table.innerHTML + `<tr>
                        <td>${responseSingleFlightDelay.Recommendations.indexOf(item) + 1}</td>
                        <td><a href="${item.url}" target="_blank">${item["Flight Number"]}</a></td>
                        <td>${item.Airline}</td>
                        <td>${item[city]}</td>
                        <td>${item.Date}</td>
                    </tr>`
            })
        }, function (e) {
            // handle errors
        });
    
    var responseAllFlights;
    makeRequest('POST', baseUrl + '/flight/allFlights', JSON.stringify({ flightId: flightNumber, date: journeyDate}))
        .then(function (e) {
            console.log(e.target.response);
            responseAllFlights = JSON.parse(e.target.response);
            // add preprocessing code and call to generate graph
        }, function (e) {
            // handle errors
        });   
}
function flight_updated(){
    
}
function LineChart(data, {
x = ([x]) => x, // given d in data, returns the (temporal) x-value
y = ([, y]) => y, // given d in data, returns the (quantitative) y-value
title, // given d in data, returns the title text
defined, // for gaps in data
curve = d3.curveLinear, // method of interpolation between points
marginTop = 20, // top margin, in pixels
marginRight = 30, // right margin, in pixels
marginBottom = 30, // bottom margin, in pixels
marginLeft = 40, // the left margin, in pixels
width = 640, // outer width, in pixels
height = 400, // outer height, in pixels
xType = d3.scaleUtc, // type of x-scale
xDomain, // [xmin, xmax]
xRange = [marginLeft, width - marginRight], // [left, right]
yType = d3.scalePoint, // type of y-scale
yDomain, // [ymin, ymax]
yRange = [height - marginBottom, marginTop], // [bottom, top]
color = "currentColor", // stroke color of line
strokeWidth = 1.5, // stroke width of line, in pixels
strokeLinejoin = "round", // stroke line join of line
strokeLinecap = "round", // stroke line cap of line
yFormat, // a format specifier string for the y-axis
yLabel, // a label for the y-axis
} = {}) {
// Compute values.
const X = d3.map(data, x);
const Y = d3.map(data, y);
const O = d3.map(data, d => d);
const I = d3.map(data, (_, i) => i);

// Compute which data points are considered defined.
if (defined === undefined) defined = (d, i) => true;
const D = d3.map(data, defined);

// Compute default domains.
if (xDomain === undefined) xDomain = [d3.min(X),d3.max(X)];
if (yDomain === undefined) yDomain = [...new Set(Y)];

// Construct scales and axes.
const xScale = xType(xDomain, xRange);
const yScale = yType(yDomain,yRange);
const xAxis = d3.axisBottom(xScale).tickSizeOuter(0).tickFormat(d3.timeFormat("%b %-d, %y"));
const yAxis = d3.axisLeft(yScale);

// Compute titles.
if (title === undefined) {
    const formatDate = d3.timeFormat("%b %-d, %y");
    title = i => `${formatDate(X[i])}\n${Y[i]}`;
} else {
    const O = d3.map(data, d => d);
    const T = title;
    title = i => T(O[i], i, data);
}

// Construct a line generator.
const line = d3.line()
    .defined(i => D[i])
    .curve(curve)
    .x(i => xScale(X[i])+12)
    .y(i => yScale(Y[i]));

const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "max-width: 100%; height: auto; height: intrinsic;background-color: whitesmoke;margin: 20px")
    .attr("font-family", "sans-serif")
    .attr("font-size", 10)
    .style("-webkit-tap-highlight-color", "transparent")
    .style("overflow", "visible")
    .on("pointerenter pointermove", pointermoved)
    .on("pointerleave", pointerleft)
    .on("touchstart", event => event.preventDefault());
svg.selectAll("circle")
    .data(I)
    .join("circle") // enter append
    .attr("r", "3")
    .attr("stroke", d =>{
        var val = Y[d];
        if(val == 'No Delay Predicted'){
            return "green";
        }
        else if(val == "Delay Upto 1 Hour Predicted"){
            return "#ffed6f";
        }
        else{
            return "red";
        }
    })
    .attr("stroke-width", 4) // radius
    .attr("cx", d=> xScale(X[d])+12)
    .attr("cy", d=> yScale(Y[d]))

svg.append("g")
    .attr("transform", `translate(0,${height - marginBottom})`)
    .call(xAxis);

svg.append("g")
    .attr("transform", `translate(${marginLeft},0)`)
    .call(yAxis)
    .call(g => g.selectAll("text").attr("transform", "translate(-10,0) rotate(-50)")
    .style("text-anchor", "end"))
    .call(g => g.select(".domain").remove())
    .call(g => g.selectAll(".tick line").clone()
        .attr("x2", width - marginLeft - marginRight)
        .attr("stroke-opacity", 0.1))
    .call(g => g.append("text")
        .attr("x", -marginLeft)
        .attr("y", 10)
        .attr("fill", "currentColor")
        .attr("text-anchor", "start")
        .text(yLabel));

svg.append("path")
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", strokeWidth)
    .attr("stroke-linejoin", strokeLinejoin)
    .attr("stroke-linecap", strokeLinecap)
    .attr("d", line(I));

const tooltip = svg.append("g")
    .style("pointer-events", "none");

function pointermoved(event) {
    const i = d3.bisectCenter(X, xScale.invert(d3.pointer(event)[0]));
    tooltip.style("display", null);
    tooltip.attr("transform", `translate(${xScale(X[i])+12},${yScale(Y[i])})`);

    const path = tooltip.selectAll("path")
    .data([,])
    .join("path")
        .attr("fill", "white")
        .attr("stroke", "black");

    const text = tooltip.selectAll("text")
    .data([,])
    .join("text")
    .call(text => text
        .selectAll("tspan")
        .data(`${title(i)}`.split(/\n/))
        .join("tspan")
        .attr("x", 0)
        .attr("y", (_, i) => `${i * 1.1}em`)
        .attr("font-weight", (_, i) => i ? null : "bold")
        .text(d => d));

    const {x, y, width: w, height: h} = text.node().getBBox();
    text.attr("transform", `translate(${-w / 2},${15 - y})`);
    path.attr("d", `M${-w / 2 - 10},5H-5l5,-5l5,5H${w / 2 + 10}v${h + 20}h-${w + 20}z`);
    svg.property("value", O[i]).dispatch("input", {bubbles: true});
}

function pointerleft() {
    tooltip.style("display", "none");
    svg.node().value = null;
    svg.dispatch("input", {bubbles: true});
}

return Object.assign(svg.node(), {value: null});
}

function BarChart(data, {
    x = (d, i) => i, // given d in data, returns the (ordinal) x-value
    y = d => d, // given d in data, returns the (quantitative) y-value
    title, // given d in data, returns the title text
    marginTop = 20, // top margin, in pixels
    marginRight = 30, // right margin, in pixels
    marginBottom = 30, // bottom margin, in pixels
    marginLeft = 40, // the left margin, in pixels
    width = 640, // the outer width of the chart, in pixels
    height = 400, // the outer height of the chart, in pixels
    xDomain, // an array of (ordinal) x-values
    xRange = [marginLeft, width - marginRight], // [left, right]
    yType = d3.scaleLinear, // y-scale type
    yDomain, // [ymin, ymax]
    yRange = [height - marginBottom, marginTop], // [bottom, top]
    xPadding = 0.1, // amount of x-range to reserve to separate bars
    yFormat, // a format specifier string for the y-axis
    yLabel, // a label for the y-axis
    color = "currentColor" // bar fill color
  } = {}) {
    // Compute values.
    const X = d3.map(data, x);
    const Y = d3.map(data, y);
  
    // Compute default domains, and unique the x-domain.
    if (xDomain === undefined) xDomain = X;
    if (yDomain === undefined) yDomain = [0, d3.max(Y)];
    xDomain = new d3.InternSet(xDomain);
  
    // Omit any data not present in the x-domain.
    const I = d3.range(X.length).filter(i => xDomain.has(X[i]));
  
    // Construct scales, axes, and formats.
    const xScale = d3.scaleBand(xDomain, xRange).padding(xPadding);
    const yScale = yType(yDomain, yRange);
    const xAxis = d3.axisBottom(xScale).tickSizeOuter(0);
    const yAxis = d3.axisLeft(yScale).ticks(height / 40, yFormat);
  
    // Compute titles.
    if (title === undefined) {
      const formatValue = yScale.tickFormat(100, yFormat);
      title = i => `${X[i]}\n${formatValue(Y[i])}`;
    } else {
      const O = d3.map(data, d => d);
      const T = title;
      title = i => T(O[i], i, data);
    }
  
    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto; height: intrinsic;background-color: whitesmoke;margin: 20px")
  
    svg.append("g")
        .attr("transform", `translate(${marginLeft},0)`)
        .call(yAxis)
        .call(g => g.select(".domain").remove())
        .call(g => g.selectAll(".tick line").clone()
            .attr("x2", width - marginLeft - marginRight)
            .attr("stroke-opacity", 0.1))
        .call(g => g.append("text")
            .attr("x", -marginLeft)
            .attr("y", 10)
            .attr("fill", "currentColor")
            .attr("text-anchor", "start")
            .text(yLabel));
  
    const bar = svg.append("g")
        .attr("fill", color)
      .selectAll("rect")
      .data(I)
      .join("rect")
        .attr("x", i => xScale(X[i]))
        .attr("y", i => yScale(Y[i]))
        .attr("height", i => yScale(0) - yScale(Y[i]))
        .attr("width", xScale.bandwidth());
  
    if (title) bar.append("title")
        .text(title);
  
    svg.append("g")
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(xAxis);
  
    return svg.node();
  }