import React, { Component } from 'react';
import TableRow from "./TableRow.js"
import {MapVideoModelToAppModel} from "./model.js"
import WebApi from './WebApi.js'

const ErrorMsg = ({msg}) => <div className="error">{msg}</div>

class UrlTable extends Component {
    constructor(props) {
        super(props) ;
        this.state = { 
            data: this.props.data,
            error: false
        }

        this.errorMsg = ""
        this.onRemoveUrl = this.onRemoveUrl.bind(this)
        this.addUrl = this.addUrl.bind(this)
        this.onError = this.onError.bind(this)
    }

    render() {
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
                            {this.state.data.map((data, index) => <TableRow key={data.uid} data={data} index={index} onRemoveUrl={this.onRemoveUrl} onError={this.onError}/>)}
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
        var fetcher = new WebApi(data => {
            this.state.data.splice(index,1)
            this.setState({data: this.props.data})
            },
            data => {this.onError("Can't delete video id:"+video_id)}
        )

        fetcher.removeVideoById(video_id)
        console.log("state:", this.state)
    }


    addUrl(video_url) {
        console.log("adddUrl:"+video_url)
        var fetcher = new WebApi(data => {
                this.props.data.push(MapVideoModelToAppModel(data))
                this.setState({data: this.props.data})
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
