



export function populateModal(){

    const container = document.getElementById("events-pick-container")
    container.innerHTML=""
    const url = `${BASE_URL}api/events`
    console.log(url)

    fetch(url)
        .then(response => response.json())
        .then(data=>{
            data.forEach(event=>{
                const card = document.createElement('event-card')
                card.setAttribute("title", event.name)

                const wrap = document.createElement("div")
                wrap.setAttribute("class", "card m-2")

                const body = document.createElement('div');
                body.setAttribute('class', 'card-body');

                const title = document.createElement('h5');
                title.setAttribute('class', 'card-title');
                title.textContent = this.getAttribute('title') || 'Event name';

                body.innerHTML=`
                <div class="row">
                    <div class="col">
                        <h4 class="card-title">${event.name}</h4>
                        <input type="checkbox" class="btn-check" id="${event.name}-check" autocomplete="off">
                        <label class="btn btn-outline-primary" for="${event.name}-check" id="${event.name}-check-label">Add</label>
                    </div>
                    <div class="col" id="${event.name}-number-box">
                        <h6>Rounds:</h6>
                        <input type="number" class="form-control" id="${event.name}-number" min="1" max="3">
                        <div id="${event.name}-round-advs">
                        </div>
                    </div>
                </div>
                `

                wrap.appendChild(body)
                container.appendChild(wrap)

                const checkbox = document.getElementById(`${event.name}-check`)
                const checkboxLabel = document.getElementById(`${event.name}-check-label`)
                const numInputBox = document.getElementById(`${event.name}-number-box`)
                const numInput = document.getElementById(`${event.name}-number`)

                numInput.addEventListener("change", ()=>{
                    const rounds = numInput.value
                    const rounds_advs = document.getElementById(`${event.name}-round-advs`)
                    let rounds_advs_content=''
                    for(let num = 1; num<=rounds;num++){
                        rounds_advs_content += `<p>Round ${num} advance: <input id="${event.name}-round-${num}" type="text" value="0" class="form-control"/></p>`
                    }
                    rounds_advs.innerHTML = rounds_advs_content
                })

                numInputBox.style.visibility = "hidden"

                checkbox.addEventListener("change", () => {
                    if (checkbox.checked) {
                        wrap.classList.add("text-bg-primary")
                        checkboxLabel.textContent="Remove"
                        checkboxLabel.classList.remove("btn-outline-primary")
                        checkboxLabel.classList.add("btn-outline-danger")
                        numInputBox.style.visibility = "visible"
                    } else {
                        wrap.classList.remove("text-bg-primary")
                        checkboxLabel.textContent="Add"
                        checkboxLabel.classList.remove("btn-outline-danger")
                        checkboxLabel.classList.add("btn-outline-primary")
                        numInputBox.style.visibility = "hidden"
                    }
                  })
                
            })
        })
        .catch(error => {
            console.error('Error:', error)
        });
}

export function postCompetition(){
    const compUrl =  `${BASE_URL}api/competitions`
    const eventsUrl = `${BASE_URL}api/events`
    const name = document.getElementById('new-competition-name').value
    
    let dataToSend = {
        competition_name: name,
        events: []
    }
    
    console.log(eventsUrl)
    fetch(eventsUrl)
        .then(response => response.json())
        .then(data => {
            data.forEach(event => {
                if(document.getElementById(`${event.name}-check`).checked){
                    const rounds = document.getElementById(`${event.name}-number`).value
                    const rounds_adncs = []
                    for(let num = 1; num<=rounds;num++){
                        rounds_adncs.push(document.getElementById(`${event.name}-round-${num}`).value)
                    }
                    const ev = {
                        name: event.name,
                        number: rounds,
                        rounds_numbers: rounds_adncs
                    }
                    dataToSend.events.push(ev)
                }

            });
            fetch(compUrl, {
                method: 'POST', 
                headers:   {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataToSend)
            })
            .then(response => response.json())
            .then(responseData =>{
                if(responseData.message !== "created"){
                    console.log("comething didnt go well")
                    alert(responseData.message)
                }
            })
        })
        .catch(error => {
            console.error('Error:', error);
        });
    
}
