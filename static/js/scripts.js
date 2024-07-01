const socket = io();
let form = null;
let input = null;
let messages = null;
let result_log = null;
let currentTab = null;

let intermediate_file_progress = null;
let migrate_progress = null;


socket.on('status', (status) => {
   if (status != null){
        //console.log(status);
        update_mysql_card(status.mysql);
        update_postgres_card(status.postgres);
        updateInputs(status.configure);
        update_metadata(status.tables);
    }
});

socket.on('log', (log) => {
    if (log != null){
        appendLogLine(result_log, log.log_level, log.message);
    }
 });

socket.on("connect", () => {
    console.log("MY ID: " + socket.id);
});


socket.on("update_progress", (progress) => {
    if (currentTab == "tuples"){
        updateProgressBar(intermediate_file_progress, progress.file_name, progress.intermediate_file_progress, progress.total);
        updateProgressBar(migrate_progress, progress.name, progress.migrate_progress, progress.total);
    }
});


socket.on("update_sequence", (table, new_value) => {
    console.log("Table: " + table);
    console.log("New Value: " + new_value);
    
    update_sequence_data(table, new_value)
});


function clickTabEvent(tab){
    currentTab = tab;
    console.log(tab);

    if (tab == "connection") {
        socket.emit('test_connections');
    }
    if (tab == "configure") {
        socket.emit('configure', null);
    }

    if(tab == "conversion"){
        socket.emit('load_metadata', false);
    }

    if (tab == "tables" || tab == "primary-keys" || tab == "constraints" || tab == "indexes" || tab == "tuples" || tab == "sequences") {
        socket.emit('load_metadata', null);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const tabs = document.querySelectorAll('.navbar-link');
    const tabContents = document.querySelectorAll('.tab-content');

    form = document.getElementById('form');
    input = document.getElementById('input');
    messages = document.getElementById('messages');
    result_log = document.getElementById("result_log");
    
    intermediate_file_progress = document.getElementById('intermediate_file_progress');
    migrate_progress = document.getElementById('migrate_progress');

    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            const tabId = this.getAttribute('data-tab');

            clickTabEvent(tabId);
            changeFilter(tabId, tabs);

            const activeTab = document.getElementById(tabId);
            tabContents.forEach(content => {
                content.classList.remove('active');
            });

            tabs.forEach(tab => {
                tab.classList.remove('active');
            });

            activeTab.classList.add('active');
            this.classList.add('active');
        });
    });
});

function BUTTON_migrate_tables() {
    socket.emit('migrate_tables');
}

function BUTTON_migrate_primary_keys() {
    socket.emit('migrate_primary_keys');
}

function BUTTON_migrate_tuples() {
    socket.emit('migrate_tuples');
}

function BUTTON_migrate_constraints() {
    socket.emit('migrate_constraints');
}

function BUTTON_migrate_indexes() {
    socket.emit('migrate_indexes');
}



function BUTTON_updateConfiguration() {

    let schema_name = document.getElementById("schema_name").value;
    let postgres_bulk_size = document.getElementById("postgres_bulk_size").value;
    let mysql_batch_size = document.getElementById("mysql_batch_size").value;

    let configData = {
        schema_name: schema_name,
        postgres_bulk_size: parseInt(postgres_bulk_size), 
        mysql_batch_size: parseInt(mysql_batch_size) 
    };

    socket.emit('configure', configData);
}


function BUTTON_load_metadata(mode) { 
    if (mode != null ) {
        
        socket.emit('load_metadata', true);
    }else{
       
        socket.emit('load_metadata', null);
    }
}


function BUTTON_load_select() { 
    socket.emit('update_table_metadata_select_all'); 
}

function BUTTON_load_deselect() {
    socket.emit('update_table_metadata_deselect_all');
}

function BUTTON_clear_metadata() {
    socket.emit('clear_metadata');
}

function BUTTON_clear_files() {
    socket.emit('clear_files');
}

function BUTTON_clear_database() {
    socket.emit('clear_database');
}


function BUTTON_update_sequence(){
    let tableName = document.getElementById("sequences-table-name");
    let sequence_input = document.getElementById("current_sequence");
    let sequence_value = sequence_input.value

    if (sequence_value == "" || sequence_value == null) {
        sequence_value = "1";
    }
    socket.emit('handle_sequences', tableName.textContent, sequence_value);
  }

function update_metadata(tables) {
    if (tables == null) {
        return;
    }
    let gridContainer = null 

    if (currentTab == 'configure') {
        gridContainer = document.getElementById('conversion'+"-grid-container");
    }else{
        gridContainer = document.getElementById(currentTab+"-grid-container");
    }
    gridContainer.innerHTML = ""; 
    

    
    console.log("Tables: " + tables.length);

    for (let i = 0; i < tables.length; i++) {
        let item = JSON.parse(tables[i]);
        //console.log(item);
        createNewItem(item, item.name);
    }
    
}

function updateInputs(configData) {
    if (configData == null) {
        return;
    }
    document.getElementById("schema_name").value = configData.schema_name;
    document.getElementById("postgres_bulk_size").value = configData.postgres_bulk_size;
    document.getElementById("mysql_batch_size").value = configData.mysql_batch_size;
}


function update_postgres_card(data) {
    if (data == null) {
        return;
    }
    const card = document.getElementById('postgres-card');
    if (card) {
        const dbname = card.querySelector('#postgres-dbname');
        const user = card.querySelector('#postgres-user');
        const host = card.querySelector('#postgres-host');
        const port = card.querySelector('#postgres-port');
        const error = card.querySelector('#postgres-error');
        
        dbname.textContent = `Database Name: ${data.POSTGRES_DBNAME}`;
        user.textContent = `Username: ${data.POSTGRES_USER}`;
        host.textContent = `Host: ${data.POSTGRES_HOST}`;
        port.textContent = `Port: ${data.POSTGRES_PORT}`;
        
       
        card.style.borderColor = data.connected ? 'green' : 'red';
        
       
        if (data.error) {
            error.textContent = `Error: ${data.error}`;
        } else {
            error.textContent = ''; 
        }
    }
}


function update_mysql_card(data) {
    if (data == null) {
        return;
    }
    const card = document.getElementById('mysql-card');
    if (card) {
        const dbname = card.querySelector('#mysql-dbname');
        const user = card.querySelector('#mysql-user');
        const host = card.querySelector('#mysql-host');
        const port = card.querySelector('#mysql-port');
        const error = card.querySelector('#mysql-error');
        
        dbname.textContent = `Database Name: ${data.MYSQL_DATABASE}`;
        user.textContent = `Username: ${data.MYSQL_USER}`;
        host.textContent = `Host: ${data.MYSQL_HOST}`;
        port.textContent = `Port: ${data.MYSQL_PORT}`;
        
       
        card.style.borderColor = data.connected ? 'green' : 'red';
        
        if (data.error) {
            error.textContent = `Error: ${data.error}`;
        } else {
            error.textContent = ''; 
        }
    }
}

function appendLogLine(log, level, line) {
    let logLine = document.createElement("div");
    logLine.textContent = level + ": " + line;
    log.appendChild(logLine);
    if (level == "ERROR") logLine.style.color = "red"
    if (level == "WARNING") logLine.style.color = "orange"
    //console.log(log.scrollTop);
    //console.log(log.scrollHeight)
    //console.log("-----");
    log.scrollTop = log.scrollHeight;
}

function createNewItem(table, itemId) {
    itemId = itemId + "_" + currentTab;
    let newItem = document.createElement("div");
    newItem.className = "item";
    let name = formatString(table.name);
    let icon = "tables";
    let type = null

    if (currentTab == "tables") {
        icon = "tables_sql";
        type = "table_commited"
        if(table.table_commited){
            icon = "tables_sql_green";
        }
    }

    if (currentTab == "primary-keys") {
        icon = "primary-keys";
        type = "primary_key_commited"
        if(table.primary_key_commited){
            icon = "primary-keys_green";
        }
    }
    
    if (currentTab == "constraints") {
        icon = "constraints";
        type = "constraints_commited"
        if(table.constraints_commited){
            icon = "constraints_green";
        }
    }

    if (currentTab == "indexes") {
        icon = "indexes";
        type = "indexes_commited"
        if(table.indexes_commited){
            icon = "indexes_green";
        }
    }

    if (currentTab == "tuples") {
        icon = "tuples";
        type = "tuples_commited"
        if(table.tuples_commited){
            icon = "tuples_green";
        }
    }


    if (currentTab == "sequences") {
        icon = "sequences";
        if(table.primary_key_commited){
            icon = "sequences_green";
        }
    }

    let action_button_icon = "remove";

    if (type != null){
        action_button_icon = "reset";
    }

    newItem.innerHTML = `
      <img src="/static/icons/${icon}.png" alt="Table Icon">
      <p>${name}</p>
      <button class="reset-btn" >
        <img class="reset-btn-img" src="/static/icons/${action_button_icon}.png" alt="reset">
      </button>
    `;
    
    newItem.id = itemId;
    newItem.addEventListener("click", function() {
        console.log("Name: " + table.name);
        console.log("Excluded: " + table.excluded);
        console.log("Table Commited: " + table.table_commited);
        console.log("Primary Key Commited: " + table.primary_key_commited);
        console.log("Constraints Commited: " + table.constraints_commited);
        console.log("Indexes Commited: " + table.indexes_commited);
        console.log("Tuples Commited: " + table.tuples_commited);
        console.log("......................")

        if (currentTab == "conversion") {
            console.log("(conversion) You clicked item: " + itemId);
            displayTableInfo(table);
        }

        if(currentTab == "sequences"){
            console.log("(sequences) You clicked item: " + itemId);
            displaySequencesInfo(table);
        }

        if(currentTab == "indexes"){
            console.log("(indexes) You clicked item: " + itemId);
            displayIndexInfo(table);
        }
    });


    let iconImage = newItem.querySelector("img");
    let button = newItem.querySelector("button");

    if (currentTab != "sequences") {
        button.addEventListener("click", function() {

        
            console.log("You clicked to remove item: " + table.name);
            if (table.excluded) {
                table.excluded = false;
            }else {
                table.excluded = true;
            }

            socket.emit('update_table_metadata', {name: table.name, excluded: table.excluded, type: type}); 
            
            
        });

        if (type != null && icon != null && !icon.includes("green")){
            button.style.display = "none";
        }


    }else{
        button.style.display = "none";
    }
    /*
    if (currentTab == "conversion" ||  currentTab == "indexes") {

        button.addEventListener("click", function() {

            if(currentTab == "conversion"){
                console.log("You clicked to remove item: " + table.name);
                if (table.excluded) {
                    table.excluded = false;
                    iconImage.src = "/static/icons/tables.png";
                }else {
                    table.excluded = true;
                    iconImage.src = "/static/icons/tables_red.png";
                }
                socket.emit('update_table_metadata', {name: table.name, excluded: table.excluded}); 
            } 
              
        });
    }else{
        button.style.display = "none";
    }
    */

    if (table.excluded) {
        iconImage.src = "/static/icons/" + icon + "_red.png";
        if (icon != null && icon.includes("green")){
            iconImage.src = "/static/icons/" + icon + ".png";
        }
    }else{
        iconImage.src = "/static/icons/" + icon + ".png";
    }

    let gridContainer = document.getElementById(currentTab+"-grid-container");
    gridContainer.appendChild(newItem);
  }
  

  function formatString(inputString) {
    if (inputString.length > 15) {
      return inputString.substring(0, 15) + "...";
    } else {
      return inputString;
    }
  }


  function displayTableInfo(data) {
    document.getElementById("conversion_table_info").style.display = "block";
    let tableName = document.getElementById("conversion-table-name");
    tableName.textContent = "Table: "+data.name;
    let tableTuples = document.getElementById("conversion-table-tuples");
    tableTuples.textContent = "Number of Tuples: "+data.num_tuples;

    if(data.columns != null)     displayColumns(data.columns);
    if(data.constraints != null) displayConstraints(data.constraints);
    if(data.indexes != null)     displayIndexes(data.indexes);
  }

  
  function displayColumns(columns) {
    let tableBody = document.querySelector('#columns-table tbody');
    tableBody.innerHTML = '';
  
    columns.forEach(function(column) {
      let row = document.createElement('tr');
      row.innerHTML = `
        <td>${column.name}</td>
        <td>${column.data_type}</td>
        <td>${column.nullable ? 'Yes' : 'No'}</td>
        <td>${column.default !== null ? column.default : 'None'}</td>
      `;
      tableBody.appendChild(row);
    });
  }
  
  function displayConstraints(constraints) {
    let tableBody = document.querySelector('#constraints-table tbody');
    tableBody.innerHTML = '';
  
    constraints.forEach(function(constraint) {
      let row = document.createElement('tr');
      row.innerHTML = `
        <td>${constraint.name}</td>
        <td>${constraint.column_name}</td>
        <td>${constraint.referenced_table_schema}</td>
        <td>${constraint.referenced_table_name}</td>
        <td>${constraint.referenced_column_name}</td>
      `;
      tableBody.appendChild(row);
    });
  }
  
  function displayIndexes(indexes) {
    let tableBody = document.querySelector('#indexes-table tbody');
    tableBody.innerHTML = '';
  
    indexes.forEach(function(index) {
      let row = document.createElement('tr');
      row.innerHTML = `
        <td>${index.name}</td>
        <td>${index.column_name}</td>
        <td>${index.nullable ? 'Yes' : 'No'}</td>
        <td>${index.index_type}</td>
        <td>${index.non_unique}</td>
      `;
      tableBody.appendChild(row);
    });
  }

  function displaySequencesInfo(data) {
    document.getElementById("sequences_table_info").style.display = "block";
    let tableName = document.getElementById("sequences-table-name");
    tableName.textContent = data.name;

    let sequence_input = document.getElementById("current_sequence");
    sequence_input.value = ""
    socket.emit('handle_sequences', data.name, null);
  }


  function displayIndexInfo(data) {
    
    document.getElementById("indexes_table_info").style.display = "block";
    let tableName = document.getElementById("indexes-table-name");
    tableName.textContent = data.name;

    indexes = data.indexes;

    document.getElementById("indexes_table_info").style.display = "block";

    let tableBody = document.querySelector('#indexes-table-with-button tbody');
    tableBody.innerHTML = '';
  
    indexes.forEach(function(index) {
        let row = document.createElement('tr');
        let checkboxId = `index_checkbox_${index.name}`;
        row.innerHTML = `
          <td>${index.name}</td>
          <td><input type="checkbox" id="${checkboxId}" name="index_checkbox" ${index.excluded ? '' : 'checked'} ${index.name === 'PRIMARY' || index.non_unique === 0 ? 'disabled' : ''}></td>
        `;
        tableBody.appendChild(row);
      
   
        let checkbox = row.querySelector(`#${checkboxId}`);
        checkbox.addEventListener('click', function() {
          let isChecked = checkbox.checked;
          console.log(`Checkbox ${index.name} clicado!`);
          socket.emit('handle_specific_index', data.name, index.name, !isChecked);

        });
      });
    
  }


  function update_sequence_data(table, new_value){
        let tableName = document.getElementById("sequences-table-name");
       
        if(table != null && table == tableName.textContent){
            let sequence_input = document.getElementById("current_sequence");
            sequence_input.value = new_value;
        }
    }


  function changeFilter(dataTab, tabs) {

    for (let i = 0; i < tabs.length; i++) {
        let tab = tabs[i];
        const element = document.getElementById(tab.getAttribute('data-tab')+"_icon");
        element.style.filter = "invert(100%)";
    }
    const element = document.getElementById(dataTab+"_icon");
    element.style.filter =  "invert(100%) sepia(100%) saturate(5500%) hue-rotate(5deg)";
    
}



// Function to update progress bar
function updateProgressBar(bar, name, tuples, total) {
    const progress = bar.querySelector('.progress');
    const label = bar.querySelector('.label');

    // Calculate progress percentage
    const percentage = (tuples / total) * 100;

    // Update progress bar width
    progress.style.width = percentage + '%';

    // Update data display
    label.querySelector('.name').textContent = name;
    label.querySelector('.data').textContent = tuples + ' / ' + total;
}

