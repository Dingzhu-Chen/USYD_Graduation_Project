
$(document).ready(function () {

    const options = {
        key: '3DnlnVLGUgBoV6ExWhuQbOLYmW8rFPuY', 
        lat: -25.67, 
        lon: 134.11, 
        zoom: 5, 
        overlay: 'temp',
        language: 'en',
        maxZoom: 18
    };

    let map;

    windyInit(options, windyAPI => {
        
        map = windyAPI.map;

    $("#dashboard-tab").click(function(){switchTab('dashboard')});
    $("#map-tab").click(function(){switchTab('bushfire-map')});

    function switchTab(tabName) {
        var i, tabcontent, tabItem;
        
        // Hide all tab content
        tabcontent = document.getElementsByClassName("tab-content");
        for (i = 0; i < tabcontent.length; i++) {
          tabcontent[i].style.display = "none";
        }
    
        // Remove 'active' class from all tab links
        tabItem = document.getElementsByClassName("tabItem");
        for (i = 0; i < tabItem.length; i++) {
          tabItem[i].className = tabItem[i].className.replace(" active", "");
        }
    
        // Show the selected tab and add 'active' class to the clicked tab
        document.getElementById(tabName).style.display = "block";
        event.currentTarget.className += " active";
        if (tabName === 'bushfire-map') {  
            setTimeout(function() {
                map.invalidateSize();
                // windymap.invalidateSize();  
            }, 100); 
        }
    }

    $.getJSON("weather", function (data) {
        loadWeatherList(data);
    });

    function loadBushfire(bushfires) {
        const bushfireList = document.getElementById('bushfireList');
        bushfires.forEach(fire => {
            const listItem = document.createElement('li');
            listItem.textContent = `${fire.location}: Date: ${fire.startDate}, Time: ${fire.startTime}`;

            const button = document.createElement('button');
            button.textContent = "Check on Map";
            button.style.marginLeft = '10px';
            button.className += "btn btn-ofx-blue";

            button.onclick = function() {
                switchTab('bushfire-map');
                map.setView([fire.coordinates.latitude, fire.coordinates.longitude], 15); 
                this.classList.remove('active')
            };

            listItem.appendChild(button);

            bushfireList.appendChild(listItem);

            let marker = L.marker([fire.coordinates.latitude, fire.coordinates.longitude], { icon: fireIcon, fire: fire });
            if (marker){
                let popupContent = `
                    <table style="font-family: Arial, sans-serif;">
                    <tr><th>Location:</th><td>${fire.location}</td></tr>
                    <tr><th>Acquire Date:</th><td>${fire.startDate}</td></tr>
                    <tr><th>Acquire Time:</th><td>${fire.startTime}</td></tr>
                </table>`;
        
                marker.on('click', function() {
                    document.getElementById('bushfireDetails').innerHTML = popupContent;
                    window.sidebar.open('details');
                });
                marker.addTo(map); 
            }
        });
    }

    // Function to populate weather conditions list
    function loadWeatherList(cityWeather) {
        const weatherList = document.getElementById('weatherList');
        cityWeather.forEach(weather => {
            const listItem = document.createElement('li');
            listItem.textContent = `${weather.city}: ${weather.weather}, Max: ${weather.maxTemperature}°C, Min: ${weather.minTemperature}°C`;
            weatherList.appendChild(listItem);
        });
    }

    // Call these functions when the page loads
    document.addEventListener('DOMContentLoaded', function() {
        loadBushfireList();
        loadWeatherList();
    });

    window.sidebar = L.control.sidebar('leafLetSidebar',{
        autopan: true,
        closeButton: false,
        container: 'leafLetSidebar',
        position: 'right'
    }).addTo(map);
    
    var properties = []
    
    fetch('/disaster_notification_system/get_user_properties/')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            data.features.forEach(feature => {
                // Ensure the coordinates are numbers and not strings
                const latitude = parseFloat(feature.geometry.coordinates[1]);
                const longitude = parseFloat(feature.geometry.coordinates[0]);
                properties.push({name: feature.properties.name, address: feature.properties.address, latitude: latitude, longitude: longitude})
            });
        })
        .catch(error => console.error('Error fetching user properties:', error));

    var propertyModal = document.getElementById("propertyModal");
    // Get the close button
    var propertyClose = document.getElementById("propertyModalClose");
    // Get the property list container
    var propertyList = document.getElementById("propertyList");

    function populateModal() {
        propertyList.innerHTML = ""; // Clear any existing content

        var propertyModalButton = document.getElementById("propertyModalButton");
        propertyModalButton.onclick = function() {
            window.location.href = '/user/properties/';
        };
      
        properties.forEach(function(property) {
            // Create a div for each property
            var propertyDiv = document.createElement("div");
            propertyDiv.style.marginBottom = "10px";
            propertyDiv.style.display = "flex";
            propertyDiv.style.justifyContent = "space-between";
            propertyDiv.style.alignItems = "center";
    
            // Create a paragraph for the property name and address
            var propertyInfo = document.createElement("p");
            propertyInfo.innerHTML = `<strong>${property.name}</strong><br>${property.address}`;
        
            // Create a button for each property to check location on map
            var checkPropertyBtn = document.createElement("button");
            checkPropertyBtn.classList.add("propertyModalButton");
            checkPropertyBtn.innerHTML = "Check on map";
            checkPropertyBtn.onclick = function() {
                moveToLocation(property.latitude, property.longitude);
            };
        
            // Append the property info and button to the propertyDiv
            propertyDiv.appendChild(propertyInfo);
            propertyDiv.appendChild(checkPropertyBtn);
        
            // Append the propertyDiv to the property list container
            propertyList.appendChild(propertyDiv);
        });
    }
    
    function moveToLocation(lat, lng) {
        // Hide the property list modal
        var propertyModal = document.getElementById("propertyModal");
        if (propertyModal) {
            propertyModal.style.display = "none"; // Hide the modal
        }
    
        // Assuming the map is globally available as "map"
        map.setView([lat, lng], 15); // Zoom to the location, 15 is a typical zoom level
        
    }

    propertyClose.onclick = function() {
        propertyModal.style.display = "none";
    };

    window.onclick = function(event) {
        if (event.target == propertyModal) {
            propertyModal.style.display = "none";
        }
    };

    L.easyButton('fa-home', function(btn, map) {
        populateModal(); // Populate the modal with properties
        propertyModal.style.display = "block"; // Show the modal
    }).addTo(map);

    var bushfireModal = document.getElementById("bushfireModal");
    // Get the close button
    var bushfireClose = document.getElementById("bushfireModalClose");
    // Get the property list container
    var pbushfireModalList = document.getElementById("bushfireModalList");

    function populateBushfireModal() {
        pbushfireModalList.innerHTML = ""; // Clear any existing content

        $.getJSON("recent_fire", function (bushfireModalLs) {
            bushfireModalLs.forEach(function(bushfire) {

                // Create a div for each property
                var bushfireDiv = document.createElement("div");
                bushfireDiv.style.marginBottom = "10px";
                bushfireDiv.style.display = "flex";
                bushfireDiv.style.justifyContent = "space-between";
                bushfireDiv.style.alignItems = "center"
            
                // Create a paragraph for the property name and address
                var bushfireInfo = document.createElement("p");
                bushfireInfo.innerHTML = `${bushfire.location}: Date: ${bushfire.startDate}, Time: ${bushfire.startTime}`;
            
                // Create a fake button for each property (could be a span or button element)
                var checkBushfireyBtn = document.createElement("button");
                checkBushfireyBtn.classList.add("bushfireModalButton");
                checkBushfireyBtn.innerHTML = "Check on map";
                checkBushfireyBtn.onclick = function() {
                    var bushfireModal = document.getElementById("bushfireModal");
                    if (bushfireModal) {
                        bushfireModal.style.display = "none"; // Hide the modal
                    }
                
                    // Assuming the map is globally available as "map"
                    map.setView([bushfire.coordinates.latitude, bushfire.coordinates.longitude], 15); 
                };
            
                // Append the property info and button to the propertyDiv
                bushfireDiv.appendChild(bushfireInfo);
                bushfireDiv.appendChild(checkBushfireyBtn);
            
                // Append the propertyDiv to the property list container
                pbushfireModalList.appendChild(bushfireDiv);
            });
        });
      
        
    };

    $.getJSON("recent_fire", function (data) {
        loadBushfire(data);
    });

    L.easyButton('fa-list', function(btn, map) {
        populateBushfireModal(); // Populate the modal with properties
        bushfireModal.style.display = "block"; // Show the modal
    }).addTo(map);

    bushfireClose.onclick = function() {
        bushfireModal.style.display = "none";
    };

    window.onclick = function(event) {
        if (event.target == bushfireModal) {
            bushfireModal.style.display = "none";
        }
    };

    L.easyButton('fa-solid fa-location-crosshairs', function(btn, map) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;
                
                // Set the map view to the current location with a zoom level
                map.setView([lat, lng], 13);
    
            }, function(error) {
                console.error("Error getting location: " + error.message);
            }, {
                enableHighAccuracy: true,  
                timeout: 10000,            
                maximumAge: 0              
            });
        } else {
            console.error("Geolocation is not supported by this browser.");
        }
    }).addTo(map);

    map.on('click', function(e) {
        // Check if the sidebar is open
        window.sidebar.close(); // Collapse the sidebar
    });

    // miles/km scale to display coordinates
    L.control.scale().addTo(map);

    // mouse coordinate tracker
    const Coordinates = L.Control.extend({
        onAdd: map => {
            const container = L.DomUtil.create("div");
            map.addEventListener("mousemove", tenement => {
                container.innerHTML = `
                      <p>Latitude: ${tenement.latlng.lat.toFixed(4)} | 
                        Longitude: ${tenement.latlng.lng.toFixed(4)}
                      </p>`;
            });
            return container;
        }
    });
    map.addControl(new Coordinates({position: "bottomleft"}));

    let fireIcon = L.icon({
        iconUrl: 'https://i.imgur.com/63rAakw.png',
        iconSize: [30, 30],
        iconAnchor: [20, 20],   // Middle 
        popupAnchor: [0, -16]   
    });

    let PredictedfireIcon = L.icon({
        iconUrl: 'https://i.imgur.com/S0b6BcO.png',
        iconSize: [30, 30],
        iconAnchor: [20, 20],   // Middle 
        popupAnchor: [0, -16]   
    });

    let houseIcon = L.icon({
        iconUrl:'https://i.imgur.com/iRPxObS.png',
        iconSize: [30, 30],
        iconAnchor: [20, 20],   // Middle 
        popupAnchor: [0, -25],
        className: '' 
    });

    let hazardsLegend = L.control.Legend({
        position: "topleft",
        title: 'Hazards',
        legends: [{
            label: 'Bushfire',
            type: "polygon",
            sides: 3, 
            fillColor:'#FF5757',
            weight: 2,
            color:'black',
        },{
            label: 'Predicted Bushfire',
            type: "polygon",
            sides: 3, 
            fillColor:'#FFDE59',
            weight: 2,
            color:'black',
        }, {
            label: 'Your Property',
            type: "image",  
            url: 'https://i.imgur.com/iRPxObS.png', 
            imageUrl: 'https://i.imgur.com/iRPxObS.png',
            weight: 2
        }]

    });

    map.addControl(hazardsLegend)

    var day1Layer = L.layerGroup();
    var day2Layer = L.layerGroup();
    var day3Layer = L.layerGroup();

    fetch('/disaster_notification_system/get_user_properties/')
    .then(response => response.json())
    .then(data => {
        data.features.forEach(feature => {
            // Ensure the coordinates are numbers and not strings
            const latitude = parseFloat(feature.geometry.coordinates[1]);
            const longitude = parseFloat(feature.geometry.coordinates[0]);

            if (!isNaN(latitude) && !isNaN(longitude)) {
                const popupContent = `
                    <table style="font-family: Arial, sans-serif;">
                        <tr><th>Name:</th><td>${feature.properties.name}</td></tr>
                        <tr><th>Address:</th><td>${feature.properties.address}</td></tr>
                    </table>`;
                
                // Add marker with appropriate icon
                let marker = L.marker([latitude, longitude], { icon: houseIcon })
                    .addTo(map)
                    .bindPopup(popupContent);
            } else {
                console.error("Invalid coordinates for property:", feature);
            }
        });
    })
    .catch(error => console.error('Error fetching user properties:', error));

    fetch('/disaster_notification_system/get_predicted_bushfire/')
    .then(response => response.json())
    .then(data => {
        data.features.forEach(feature => {
            // Ensure the coordinates are numbers and not strings
            const latitude = parseFloat(feature.geometry.coordinates[1]);
            const longitude = parseFloat(feature.geometry.coordinates[0]);

            if (!isNaN(latitude) && !isNaN(longitude)) {
                const popupContent = `
                    <table style="font-family: Arial, sans-serif;">
                        <tr><th>Predicted bushfire</td></tr>
                    </table>`;
                
                // Add marker with appropriate icon
                let marker = L.marker([latitude, longitude], { icon: PredictedfireIcon })
                    .addTo(map)
                    .bindPopup(popupContent);
            } else {
                console.error("Invalid coordinates for property:", feature);
            }
        });
    })
    .catch(error => console.error('Error fetching user properties:', error));

    $.getJSON("get_predicted_bushfire_path", function (data) {
        data.features.forEach(feature => {
            const latitude = parseFloat(feature.geometry.coordinates[1]);
            const longitude = parseFloat(feature.geometry.coordinates[0]);

            const popupContent = `
            <table style="font-family: Arial, sans-serif;">
                <tr><th>Predicted bushfire</td></tr>
            </table>`;

            let marker = L.marker([latitude, longitude], { icon: PredictedfireIcon }).bindPopup(popupContent);

            let selectedLayer;

            if(feature.day === 1 ){
                marker.addTo(day1Layer);
                feature.parents.forEach( p => {
                    const lat = parseFloat(feature.geometry.coordinates[1]);
                    const lon = parseFloat(feature.geometry.coordinates[0]);
                    L.polyline([[lon,lat], [longitude,latitude]],{
                        color: 'blue',
                    }).arrowheads({
                        yawn: 40,
                    }).addTo(day1Layer);
                }) 
            }else if(feature.day === 2 ){
                marker.addTo(day2Layer);
                feature.parents.forEach( p => {
                    const lat = parseFloat(feature.geometry.coordinates[1]);
                    const lon = parseFloat(feature.geometry.coordinates[0]);
                    L.polyline([[lon,lat], [longitude,latitude]],{
                        color: 'blue'
                    }).arrowheads({
                        yawn: 40,
                    }).addTo(day2Layer);
                }) 
            }else if(feature.day === 3 ){
                marker.addTo(day3Layer);
                feature.parents.forEach( p => {
                    const lat = parseFloat(feature.geometry.coordinates[1]);
                    const lon = parseFloat(feature.geometry.coordinates[0]);
                    L.polyline([[lon,lat], [longitude,latitude]],{
                        color: 'blue'
                    }).arrowheads({
                        yawn: 40,
                    }).addTo(day3Layer);
                }) 
            }
        });

    });


    var overlayMaps = {
        "1 day later": day1Layer,
        "2 day later": day2Layer,
        "3 day later": day3Layer
    };

    L.control.layers(null, overlayMaps, { collapsed: true, position: 'topleft' }).addTo(map);
    day1Layer.addTo(map);

    $('#sidebarToggleButton').on('click',function (e) {             // resize map if side bar changes size
        setTimeout(function(){map.invalidateSize()}, 200);
    });
});
});