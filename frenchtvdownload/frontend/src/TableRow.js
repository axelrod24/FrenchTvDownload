import React, { Component } from 'react';
import { MapVideoModelToAppModel } from "./model.js"
import { moment } from 'moment'


const Item = ({classname, value, style}) => <td className={classname} style={style}>{value}</td>
const Button = ({classname, value, style, onClick}) => <button className={classname} style={style} onClick={onClick}>{value}</button>
const ButtonItem = ({classname, value, style, onClick}) => <Item className={classname} style={style} value={<button> onClick={onClick}>{value}</button>} />

const MetaDataTable = ({data}) => {
                    return (
                          <table className="matadata-table">
                            <tbody>
                              <tr>
                                <td style={{width: "80px"}}>Title:</td><td>{data.metadata.progTitle}</td>
                              </tr>
                              <tr>
                                <td>Name:</td><td>{data.metadata.progName}</td>
                              </tr>
                              <tr>
                                <td>Duration:</td><td>{(() => {
                                    var h = Math.floor(data.metadata.duration/3600)
                                    var rs = data.metadata.duration - (h*3600)
                                    var m = Math.floor(rs/60)
                                    rs = rs - (m*60)
                                    return (""+h+":"+m+":"+rs) })()}</td>
                              </tr>
                              <tr>
                                <td>Synopsis:</td><td>{data.metadata.synopsis}</td>
                              </tr>
                              <tr>
                                <td>Filename:</td><td>{data.metadata.filename}</td>
                              </tr>
                              <tr>
                                <td>Manifest:</td><td><a href={data.metadata.manifest}>{data.metadata.manifest}</a></td>
                              </tr>
                            </tbody>
                          </table>
                          ) 
                  }

class TableRow extends Component {
    constructor(props) {
        super(props) ;

        this.data = this.props.data
        this.interval = null
        this.state = {
            status: this.props.data.status,
            showMetadata: false,
            progress: -1
        }

        this.onDownloadVideo = this.onDownloadVideo.bind(this)
        this.onCancelDownload = this.onCancelDownload.bind(this)
        this.onClick = this.onClick.bind(this)
        this.onUpdateStatus = this.onUpdateStatus.bind(this)
    }

    render() {

        var statusText, statusBgColor ;

        switch(this.state.status) {
            case "done":
                statusText = "Done" 
                statusBgColor = "Aquamarine" 
            break ;

            case "pending":
                statusText = "Pending"
                statusBgColor = "CornflowerBlue"
            break ;

            case "downloading":
                statusText = "" + ((this.state.progress===-1) ? "..." : ""+this.state.progress)
                statusBgColor = "Plum"
            break ;
            
            case "not_availabl":
                statusText = "Not Available"
                statusBgColor = "greenyellow"
            break ;

            default:
                statusText = "Unknown"
                statusBgColor = "red"
            break ;
        }

        const moment = require('moment');
        return ( 
          <tr>
            <Item value={this.data.uid} />
            <td className="url" >
              <div onClick={this.onClick}>{this.data.url}</div>
              {(this.state.showMetadata) ? <MetaDataTable data={this.data} /> : null}
            </td>
            <Item value={moment(this.data.timestamp).format("ddd DD MMM YY [ - ] hh:mm:ss a")}/>
            <Item value={statusText} style={{background: statusBgColor}}/>
            <td>
                {(this.state.status==="downloading") ? 
                    <Button value="Cancel" onClick={this.onCancelDownload}/> : <Button value="Remove" onClick={() => this.props.onRemoveUrl(this.props.index)}/>}
                {(this.state.status==="pending") && <Button value="Download" onClick={this.onDownloadVideo}/>}
            </td>
          </tr>
        )
    }

    componentDidMount() {
        if (this.state.status === "downloading" && this.interval == null) {
            this.interval = setInterval(this.onUpdateStatus, 2000)
            return 
       }
    }

    componentDidUpdate(prevProps, prevState)
    {
        console.log("componentDidUpdate:",this.data.uid)
        console.log("this.state",this.state)
        if (this.interval == null) {

            if (this.state.status === "downloading") 
                this.interval = setInterval(this.onUpdateStatus, 2000)
        } else {

            if (this.state.status === "done")
                clearInterval(this.interval)
        }
   }

   componentWillUnmount()
   {
        if (this.interval != null)
            clearInterval(this.interval)
   } 

    onDownloadVideo() {
        console.log("onDownloadVideo:",this.props.index,":",this.data.uid)
        var url = "http://localhost:5000/api/download/"+this.data.uid
        fetch(url)
        .then(res => res.json())
        .then(data => {
                this.setState({status: data.status})
              })
        .catch(error => console.log('Request failed', error))  
    }

    onUpdateStatus() {
        console.log("onUpdateStatus:",this.props.index,":",this.data.uid)
        var url = "http://localhost:5000/api/status/"+this.data.uid
        fetch(url)
        .then(res => res.json())
        .then(data => {
            data = JSON.parse(data.status)
            
            if (data.status === "done") {
                fetch("http://localhost:5000/api/video/"+this.data.uid)
                .then(res => res.json())
                .then(data => {
                        this.data = MapVideoModelToAppModel(data)
                        this.setState({status: "done"})
                      })
                .catch(error => console.log('Request failed', error))  
        
            }
            if (data.status !== "no_update")
                this.setState({status:  data.status})
            if (data.status === "downloading")
                this.setState({progress: data.progress})
            
        })
        .catch(error => console.log('Request failed', error))  
    }

    onCancelDownload() {
        console.log("onCancelDownload:",this.props.index,":",this.data.uid)
        var url = "http://localhost:5000/api/download/"+this.data.uid
        fetch(url, {method: "DELETE"})
        .then(res => res.json())
        .then(data => {
            if (this.interval != null) {
                console.log("Clear interval:", this.interval)
                clearInterval(this.interval)
            }
            this.setState({status: "pending", progress: -1})
        })
        .catch(error => console.log('Request failed', error))  
      }

    onClick() {
      this.setState({showMetadata: !this.state.showMetadata})
    }
}

export default TableRow ;

