$(document).ready(async () => {
  let obj = await $.getJSON(`data.json?nocache=${new Date().getTime()}`)
  let data = obj.data
  let ts = obj.ts
  let app = new Vue({
    el: '#app',
    data () {
      return {
        data: data,
        currentSort:'stateName',
        currentSortDir:'asc',
        stateSortIcon:' ',
        totalSortIcon:' ',
        infectedSortIcon:' ',
        curedSortIcon:' ',
        deathSortIcon: ' ',
        updateTimestamp: ts
      }
    },
    methods: {
      sort:function(s) {
        if(s === this.currentSort) {
          this.currentSortDir =
          this.currentSortDir==='asc'?'desc':'asc';
        }
        var currentSortIcon =
          this.currentSortDir==='asc'?'▴':'▾';
        this.currentSort = s

        this.stateSortIcon = ' '
        this.totalSortIcon = ' '
        this.infectedSortIcon = ' '
        this.curedSortIcon = ' '
        this.deathSortIcon = ' '

        if(s === 'totalInfectedState') this.totalSortIcon = currentSortIcon
        else if(s === 'stateName') this.stateSortIcon = currentSortIcon        
        else if(s === 'infected') this.infectedSortIcon = currentSortIcon
        else if(s === 'cured') this.curedSortIcon = currentSortIcon
        else if(s === 'death') this.deathSortIcon = currentSortIcon
      },
      loadMap: function () {
        let deChart = echarts.init(document.getElementById('mapContainer'))
        let options = {
          grid: {
            left: '2%',
            right: '2%'
          },
          tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            borderColor: '#aaa',
            borderWidth: 1,
            formatter: (params, ticket, callback) => {
              let name = params.name
              let d = this.data.find(d => d.stateName === name)
              if (d) {
                let html = `
                  <div style="color: black; font-size: 12px; padding: 3px; text-align: left;">
                    ${name}
                    <hr style="margin: 1px; padding: 0px;"/>
                    现存确诊： <span style="color: #BB0000;">${d.infected}</span>
                    <br/>
                    治愈人数： <span style="color: #2B7D2B;">${d.cured}</span>
                  </div>
                `
                return html
              }
            }
          },
          visualMap: {
            orient: 'horizontal',
            left: 'center',
            min: 0,
            max: this.maxInfectedNumber,
            text: [`最高：${this.maxInfectedNumber}`, `最低：${this.minInfectedNumber}`],
            realtime: false,
            range: [1, this.maxInfectedNumber],
            inRange: {
              color: ['#FABD64', '#BB0000']
            },
            outOfRange: {
              color: ['#FFF']
            }
          },
          series: [{
            mapType: '德国',
            data: this.visualData,
            type: 'map',
            roam: false,
            name: '现存确诊',
            label: {
              show: true,
              formatter: '{c}'
            },
            nameMap: {
              'Baden-Württemberg': 'Baden-Württemberg',
              'Free State of Bavaria': 'Bayern',
              'Berlin': 'Berlin',
              'Brandenburg': 'Brandenburg',
              'Bremen': 'Bremen',
              'Hamburg': 'Hamburg',
              'Hesse': 'Hessen',
              'Mecklenburg-Vorpommern': 'Mecklenburg-Vorpommern',
              'Lower Saxony': 'Niedersachsen',
              'North Rhine-Westphalia': 'Nordrhein-Westfalen',
              'Rhineland-Palatinate': 'Rheinland-Pfalz',
              'Saarland': 'Saarland',
              'Saxony': 'Sachsen',
              'Saxony-Anhalt': 'Sachsen-Anhalt',
              'Schleswig-Holstein': 'Schleswig-Holstein',
              'Thuringia': 'Thüringen'
            }
          }]
        }
        deChart.setOption(options)
      }
    },
    computed: {
      totalInfected () {
        if (this.data && this.data.length > 0) {
          return this.data.map(d => d.infected).reduce((cur, acc) => cur + acc)
        }
        return 0
      },
      totalCured () {
        if (this.data && this.data.length > 0) {
          return this.data.map(d => d.cured).reduce((cur, acc) => cur + acc)
        }
        return 0
      },
      totalDeath () {
        if(this.data && this.data.length > 0) {
          return this.data.map(d => d.death).reduce((cur, acc) => cur + acc)
        }
        return 0
      },
      maxInfectedNumber () {
        if (this.data) {
          return Math.max(...this.data.map(d => d.infected))
        }
        return 0
      },
      minInfectedNumber () {
        if (this.data) {
          return Math.min(...this.data.map(d => d.infected))
        }
        return 0
      },
      stateSortDir () {
        if(this.currentSort === 'totalInfectedState') this.totalSortDir = currentSortIcon
        if(s === 'totalInfectedState') this.totalSortDir = currentSortIcon
        else if(s === 'stateName') this.stateSortDir = currentSortIcon        
        else if(s === 'infected') this.infectedSortDir = currentSortIcon
        else if(s === 'cured') this.curedSortDir = currentSortIcon
      },
      sortedData:function() {
        return this.data.sort((a,b) => {
          let modifier = 1;
          if(this.currentSortDir === 'desc') modifier = -1;
          if(a[this.currentSort] < b[this.currentSort]) return -1 * modifier;
          if(a[this.currentSort] > b[this.currentSort]) return 1 * modifier;

          if(this.currentSort==='totalInfectedState') {
            if(a.infected+a.cured < b.infected+b.cured) return -1 * modifier;
            if(a.infected+a.cured > b.infected+b.cured) return 1 * modifier;
          }
          return 0;
        });
      },
      visualData () {
        if (this.data) {
          return this.data.map(d => {
            return {
              name: d.stateName, 
              value: d.infected,
              data: d
            }
          })
        }
        return []
      }
    },
    filters: {
      toDEDate: function (ts) {
        if (ts) {
          return new Date(ts).toLocaleDateString("de-DE")
        }
        return 'n.a.'
      }
    },
    mounted () {
      setTimeout(() => {
        this.loadMap()
      }, 500)
    }
  })
})