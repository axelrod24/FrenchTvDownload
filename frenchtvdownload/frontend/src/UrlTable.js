import React, { Component } from 'react';
import TableRow from "./TableRow.js"
import {MapVideoModelToAppModel} from "./model.js"
import WebApi from './WebApi.js'

const InfoMsg = ({msg, isError=false}) => {
    var cn = "info"
    if (isError)
        cn = "error"
        
    return (<div className={cn}>{msg}</div>)
}

class UrlTable extends Component {
    constructor(props) {
        super(props) ;

        this.store = this.props.store
        this.state = { 
            info: false,
            error: false
        }

        this.infoMsg = ""
        this.onRemoveUrl = this.onRemoveUrl.bind(this)
        this.addUrl = this.addUrl.bind(this)
        this.onError = this.onError.bind(this)
        this.clearInfoMsg = this.clearInfoMsg.bind(this)
    }

    render() {
        console.log("UrlTable: render")
        return (
            <div> 
                {(this.state.info) ? <InfoMsg msg={this.infoMsg} isError={this.state.error}/> : <div />}       
                <div className="people">
                    <table>
                        <thead>
                            <tr>
                                <th>Id</th>
                                <th>Url</th>
                                <th>Timestamp</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(this.store.getState()) ? 
                                this.store.getState().data.map((data, index) => <TableRow key={data.uid} store={this.store} index={index} onRemoveUrl={this.onRemoveUrl} onError={this.onError}/>) : 
                                <tr><td><div>Loading table ...</div></td></tr>}
                        </tbody>
                    </table>
                </div>
            </div> 
        )
    }

    componentDidUpdate(prevProps, prevState)
    {
        console.log("componentDidUpdate")
        console.log("this.state",this.state)
        if (this.state.error) {
            setTimeout(() => {this.clearInfoMsg()}, 3000)
        }
    }

    onRemoveUrl(index, video_id) {
        console.log("onRemoveUrl:"+video_id)
        var fetcher = new WebApi(
            data => {
                this.store.dispatch({type:"REMOVE_URL", payload:video_id})
                // force render ...
                this.clearInfoMsg()
            },
            data => {this.onError("Can't delete video id:"+video_id)}
        )

        fetcher.removeVideoById(video_id)
        console.log("state:", this.state)
    }


    addUrl(video_url) {
        console.log("adddUrl:"+video_url)
        var fetcher = new WebApi(
            data => {
                this.store.dispatch({type:"ADD_URL", payload:MapVideoModelToAppModel(data)})
                // force render ...
                this.clearInfoMsg()
            },
        
            data => {this.onError("Duplicated URL : "+video_url)}
        )

        fetcher.addVideoUrl(video_url)
        this.onInfo("Adding URL "+video_url)
    }  
    
    onError(errorMsg) {
        this.infoMsg = errorMsg
        this.setState({info: true, error: true})
    }

    onInfo(infoMsg) {
        this.infoMsg = infoMsg
        this.setState({info: true})
    }

    clearInfoMsg() {
        this.setState({info: false, error: false})
    }
}

export default UrlTable ;
