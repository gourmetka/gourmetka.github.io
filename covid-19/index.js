let data = [
  {
    id: 1,
    stateName: 'Baden-Württemberg',
    geo: [0, 0],
    infected: 37,
    cured: 0,
    death: 0
  }, {
    id: 2,
    stateName: 'Bayern',
    geo: [0, 0],
    infected: 36,
    cured: 14,
    death: 0
  }, {
    id: 3,
    stateName: 'Berlin',
    geo: [0, 0],
    infected: 6,
    cured: 0,
    death: 0
  }, {
    id: 4,
    stateName: 'Brandenburg',
    geo: [0, 0],
    infected: 1,
    cured: 0,
    death: 0
  }, {
    id: 5,
    stateName: 'Bremen',
    geo: [0, 0],
    infected: 3,
    cured: 0,
    death: 0
  }, {
    id: 6,
    stateName: 'Hamburg',
    geo: [0, 0],
    infected: 4,
    cured: 0,
    death: 0
  }, {
    id: 7,
    stateName: 'Hessen',
    geo: [0, 0],
    infected: 12,
    cured: 0,
    death: 0
  }, {
    id: 8,
    stateName: 'Mecklenburg-Vorpommern',
    geo: [0, 0],
    infected: 2,
    cured: 0,
    death: 0
  }, {
    id: 9,
    stateName: 'Niedersachsen',
    geo: [0, 0],
    infected: 4,
    cured: 0,
    death: 0
  }, {
    id: 10,
    stateName: 'Nordrhein-Westfalen',
    geo: [0, 0],
    infected: 100,
    cured: 0,
    death: 0
  }, {
    id: 11,
    stateName: 'Rheinland-Pfalz',
    geo: [0, 0],
    infected: 7,
    cured: 0,
    death: 0
  }, {
    id: 12,
    stateName: 'Saarland',
    geo: [0, 0],
    infected: 1,
    cured: 0,
    death: 0
  }, {
    id: 13,
    stateName: 'Sachsen',
    geo: [0, 0],
    infected: 1,
    cured: 0,
    death: 0
  }, {
    id: 14,
    stateName: 'Sachsen-Anhalt',
    geo: [0, 0],
    infected: 0,
    cured: 0,
    death: 0
  }, {
    id: 15,
    stateName: 'Schleswig-Holstein',
    geo: [0, 0],
    infected: 3,
    cured: 0,
    death: 0
  }, {
    id: 16,
    stateName: 'Thüringen',
    geo: [0, 0],
    infected: 1,
    cured: 0,
    death: 0
  },
]

$(document).ready(() => {
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
        curedSortIcon:' '
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

        if(s === 'totalInfectedState') this.totalSortIcon = currentSortIcon
        else if(s === 'stateName') this.stateSortIcon = currentSortIcon        
        else if(s === 'infected') this.infectedSortIcon = currentSortIcon
        else if(s === 'cured') this.curedSortIcon = currentSortIcon
      },
      loadMap: function () {
        let deChart = echarts.init(document.getElementById('mapContainer'))
        let options = {
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
                    <br/>
                  </div>
                `
                return html
              }
            }
          },
          visualMap: {
            min: 0,
            max: this.maxInfectedNumber,
            text: ['High', 'Low'],
            realtime: false,
            range: [1, this.maxInfectedNumber],
            inRange: {
              color: ['#FABD64', '#BB0000'],
              symbolSize: [30, 100]
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
              show: false,
              formatter: '{b}: {c}'
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
      maxInfectedNumber () {
        if (this.data) {
          return Math.max(...this.data.map(d => d.infected))
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
    mounted () {
      setTimeout(() => {
        this.loadMap()
      }, 500)
    }
  })
})