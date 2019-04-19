import React, { Component } from 'react';
import { MapVideoModelToAppModel } from "./model.js"
import { moment } from 'moment'
import WebApi from './WebApi.js';


const Item = ({classname, value, style}) => <td className={classname} style={style}>{value}</td>
const Button = ({classname, value, style, onClick}) => <button className={classname} style={style} onClick={onClick}>{value}</button>
const ButtonItem = ({classname, value, style, onClick}) => <Item className={classname} style={style} value={<button> onClick={onClick}>{value}</button>} />

const MetaDataTable = ({data}) => {
        // if (data.status==="error") {
        //     return (
        //         <table className="matadata-table, error">
        //             <tbody>
        //                 <tr>
        //                     <td style={{width: "80px"}}>{data.metadata.errorMsg}</td>
        //                 </tr>
        //             </tbody>
        //         </table>
        //     )
        // }

        return (
            <table className="matadata-table">
            <tbody>
                {(data.metadata.errorMsg) ? <tr>
                    <td style={{background: "linear-gradient(to bottom, rgb(189, 74, 101) 0%, rgb(190, 126, 146) 100%)"}}>{data.metadata.errorMsg}</td>
                    </tr> : <span/> }
                <tr>
                {/* <td style={{width: "80px"}}>Title:</td><td>{data.metadata.progTitle}</td> */}
                <td>Title:</td><td>{data.metadata.progTitle}</td>
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
                <tr>
                <td>Video:</td><td>{data.metadata.videoFullpath}</td>
                </tr>
            </tbody>
            </table>
            ) 
    }

class TableRow extends Component {
    constructor(props) {
        super(props) ;

        this.store = this.props.store
        this.data = this.store.getState().data[this.props.index]

        this.interval = null
        this.state = {
            status: this.data.status,
            showMetadata: false,
            progress: -1
        }

        this.onDownloadVideo = this.onDownloadVideo.bind(this)
        this.onCancelDownload = this.onCancelDownload.bind(this)
        this.onClick = this.onClick.bind(this)
        this.onUpdateStatus = this.onUpdateStatus.bind(this)
    }

    render() {
        console.log("TableRow: render")
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
            
            case "not_available":
                statusText = "Not Available"
                statusBgColor = "greenyellow"
            break ;

            case "error":
                statusText = "Error"
                statusBgColor = "red"
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
                    <Button value="Cancel" onClick={this.onCancelDownload}/>
                    : <Button value="Remove" onClick={() => this.props.onRemoveUrl(this.props.index, this.data.uid)}/>}
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
        console.log("TableRow: store:",this.store.getState().data)
        if (this.interval == null) {

            if (this.state.status === "downloading") 
                this.interval = setInterval(this.onUpdateStatus, 2000)
            return
        }
        
        if (this.state.status === "done")
        {
            if (this.interval != null) {
                clearInterval(this.interval)
                this.interval = null
            }        
        }
   }

   componentWillUnmount()
   {
        if (this.interval != null) {
            clearInterval(this.interval)
            this.interval = null
        }
   } 

    onDownloadVideo() {
        console.log("onDownloadVideo:",this.props.index,":",this.data.uid)
        var fetcher = new WebApi(
            data => {
                this.store.dispatch({type:"UPDATE_STATUS", payload:{id:this.data.uid, status:data.status}})
                this.setState({status: data.status})
            },

            data => { this.props.onError(data)}
        )
        
        fetcher.downloadVideoById(this.data.uid)  
    }

    onUpdateStatus() {
        console.log("onUpdateStatus:",this.props.index,":",this.data.uid)
        var fetcher = new WebApi(
            data => {
                data = JSON.parse(data.status)
                
                switch (data.status) 
                {
                    case "done": 
                        var fetcher = new WebApi(
                            data => {
                                this.data = MapVideoModelToAppModel(data)
                                this.store.dispatch({type:"REPLACE_URL", payload: this.data})
                                this.store.dispatch({type:"UPDATE_STATUS", payload: {id:this.data.uid, status:"done"}})
                                this.setState({status: "done"})
                            },
                            data => {this.props.onError(data)}
                        )

                        fetcher.getVideoById(this.data.uid)
                        return

                    // in case of downlaod error, clear update interval and mark url as error
                    case "error":
                        if (this.interval != null) {
                            console.log("Clear interval:", this.interval)
                            clearInterval(this.interval)
                            this.interval = null
                        }
                        this.store.dispatch({type:"UPDATE_MDATA", payload:{id:this.data.uid, mdata:{errorMsg:data.message}}})
                        this.store.dispatch({type:"UPDATE_STATUS", payload:{id:this.data.uid, status:"error"}})
                        this.setState({status: "error"})
                        return
    
                    case "downloading":
                        this.setState({progress: data.progress})
                        return

                    case "no_update":
                        // this.setState({status:  data.status})
                        return

                    case "interrupted":
                        if (this.interval != null) {
                            console.log("Clear interval:", this.interval)
                            clearInterval(this.interval)
                            this.interval = null
                        }
                        this.setState({status: "pending", progress: -1})
                        this.store.dispatch({type:"UPDATE_STATUS", payload:{id:this.data.uid, status:"pending"}})
                        return
                }
            },
            data => { this.props.onError(data) }
          )
        
        fetcher.getDownloadStatusById(this.data.uid)
    }

    onCancelDownload() {
        console.log("onCancelDownload:",this.props.index,":",this.data.uid)
        var fetcher = new WebApi(
            data => {
                // if (this.interval != null) {
                //     console.log("Clear interval:", this.interval)
                //     clearInterval(this.interval)
                // }
                // this.setState({status: "pending", progress: -1})
                // this.store.dispatch({type:"UPDATE_STATUS", payload:{id:this.data.uid, status:"pending"}})
            },
            data => {this.props.onError(data)}
        )
        
        fetcher.cancelDownloadById(this.data.uid)
    }

    onClick() {
      this.setState({showMetadata: !this.state.showMetadata})
    }
}

export default TableRow ;

