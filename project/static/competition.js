export function fetchData(round_id){
    const roundUrl = new URL(`${BASE_URL}api/averages`)
    console.log("daaaaa")

}

export function populateOffcanvas(){
    const container = document.getElementById("events-offcanvas-body")
    const navName = document.getElementById("competition-navbar")
    const foobarName = document.getElementById("events-offcanvas-lable")
    const getUrl = new URL(`${BASE_URL}api/competitions`)
    const roundsUrl = new URL(`${BASE_URL}api/rounds`)
    const presentUrl = new URLSearchParams(window.location.search)
    const compId = presentUrl.get('id')
    getUrl.searchParams.append('competition_id', compId)
    fetch(getUrl)
        .then(response => response.json())
        .then(data => {
            const competition = data[0]
            console.log(competition)
            navName.textContent = competition.name
            foobarName.textContent = competition.name
            const events = competition.events
            events.forEach(event =>{
                const evWrap = document.createElement('div')
                const evName = document.createElement('button')
                const evCollapse = document.createElement('div')

                evWrap.setAttribute("class", "list-group mb-1")
                
                evName.setAttribute("class", "list-group-item list-group-item-action list-group-item-secondary active ")
                evName.setAttribute("data-bs-toggle", "collapse")
                evName.setAttribute("data-bs-target", `#${event.name}-collapse`)
                evName.setAttribute("aria-expanded", "false")
                evName.setAttribute("aria-controls", `${event.name}-collapse`)
                evName.style.borderRadius = "0px"
                evName.textContent = event.name


                evCollapse.setAttribute("class", "collapse")
                evCollapse.id = `${event.name}-collapse`

                roundsUrl.searchParams.append("competition_id", competition.id)
                roundsUrl.searchParams.append("event_id", event.id)
                fetch(roundsUrl)
                    .then(response => response.json())
                    .then(roundData =>{
                        
                        roundData.forEach(r=>{
                            const roundBtn = document.createElement('button')
                            roundBtn.setAttribute("class", "list-group-item list-group-item-action ")
                            roundBtn.textContent = `${r.number}. Round`
                            roundBtn.onclick = fetchData(r.id)
                            evCollapse.appendChild(roundBtn)
                        })
                    })

                evWrap.appendChild(evName)
                evWrap.appendChild(evCollapse)
                container.appendChild(evWrap)

            })
        })
}

export function populateNavTab(){
    const container = document.getElementById("event-selector")
    const navName = document.getElementById("nav-brand")
    const getUrl = new URL(`${BASE_URL}api/competitions`)
    
    const presentUrl = new URLSearchParams(window.location.search)

    const compId = presentUrl.get('id')
    getUrl.searchParams.append('competition_id', compId)

    fetch(getUrl)
        .then(response => response.json())
        .then(data => {
            const competition = data[0]
            console.log(competition)
            navName.textContent = competition.name
            const events = competition.events
            events.forEach(event =>{
                const evTab = document.createElement('li')
                evTab.setAttribute("class", " nav-item ")

                const evBtn = document.createElement('button')
                evBtn.setAttribute("class", "nav-link")
                evBtn.textContent = event.name
                evBtn.onclick=()=>{
                }

                evTab.appendChild(evBtn)


                
                
                container.appendChild(evTab)

                
                // roundsUrl.searchParams.append("competition_id", competition.id)
                // roundsUrl.searchParams.append("event_id", event.id)
                // fetch(roundsUrl)
                //     .then(response => response.json())
                //     .then(roundData =>{
                        
                //         roundData.forEach(r=>{
                //             const roundWrap = document.createElement('li')
                //             const roundBtn = document.createElement('button')
                //             roundBtn.setAttribute("class", "dropdown-item btn")
                //             roundBtn.textContent = `${r.number}. Round`
                //             roundBtn.onclick = ()=>fetchData(r.id)
                //             roundWrap.appendChild(roundBtn)
                //             evMenu.appendChild(roundWrap)
                //         })
                //     })

            //     evWrap.appendChild(evName)
            //     evWrap.appendChild(evCollapse)
                

            })
        })
}

function drawTables(competition_id, event_id){
    const dcontainer = document.getElementById('data-container')
    dcontainer.innerHTML=''
    const roundsUrl = new URL(`${BASE_URL}api/rounds`)
    roundsUrl.searchParams.append("competition_id", competition_id)
    roundsUrl.searchParams.append("event_id", event_id)
    fetch(roundsUrl)
        .then(response => response.json())
        .then(roundData =>{
            
            roundData.forEach(r=>{
                const avgs = getAvgs(r.id)
                const tContainer = document.createElement('div')
                tContainer.classList.add("m-5")
                tContainer.classList.add("text-center")
                if(!avgs){
                tContainer.innerHTML=`
                    <h3>${r.number}. Round</h3>
                    <h4>No data yet</h4>
                `
                dcontainer.appendChild(tContainer)
                }

            })
        })
    

}

function getAvgs(round_id){
    const avgsUrl = new URL(`${BASE_URL}api/averages`)
    fetch(avgsUrl)
        .then(response => response.json())
        .then(data =>{
            console.log(data)
            return(data)
            })
}