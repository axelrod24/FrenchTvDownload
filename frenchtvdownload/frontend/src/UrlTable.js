import React, { Component } from 'react';
import TableRow from "./TableRow.js"
import {MapVideoModelToAppModel} from "./model.js"
import WebApi from './WebApi.js'

const ErrorMsg = ({msg}) => <div className="error">{msg}</div>

class UrlTable extends Component {
    constructor(props) {
        super(props) ;

        this.store = this.props.store
        this.state = { 
            error: false
        }

        this.errorMsg = ""
        this.onRemoveUrl = this.onRemoveUrl.bind(this)
        this.addUrl = this.addUrl.bind(this)
        this.onError = this.onError.bind(this)
    }

    render() {
        console.log("UrlTable: render")
        return (
            <div>        
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
                {(this.state.error) ? <ErrorMsg msg={this.errorMsg}/> : <div />}
            </div> 
        )
    }

    componentDidUpdate(prevProps, prevState)
    {
        console.log("componentDidUpdate")
        console.log("this.state",this.state)
        if (this.state.error) {
            setTimeout(() => {this.setState({error: false})}, 3000)
        }
    }

    onRemoveUrl(index, video_id) {
        console.log("onRemoveUrl:"+video_id)
        var fetcher = new WebApi(
            data => {
                this.store.dispatch({type:"REMOVE_URL", payload:video_id})
                // force render ...
                this.setState({error: false})
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
                this.setState({error: false})
            },
        
            data => {this.onError("Duplicated URL : "+video_url)}
        )

        fetcher.addVideoUrl(video_url)
    }  
    
    onError(errorMsg) {
        this.errorMsg = errorMsg
        this.setState({error: true})
    }
}

export default UrlTable ;
