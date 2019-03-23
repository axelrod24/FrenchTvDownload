import React, { Component } from 'react';
import TableRow from "./TableRow.js"
import {UrlModel, VideoMetaData} from "./model.js"

class UrlTable extends Component {
    constructor(props) {
        super(props) ;
        this.state = { 
            data: this.props.data
        }

        this.onRemoveUrl = this.onRemoveUrl.bind(this)
        this.addUrl = this.addUrl.bind(this)
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
                            {this.state.data.map((data, index) => <TableRow key={data.uid} data={data} index={index} onRemoveUrl={this.onRemoveUrl}/>)}
                        </tbody>
                    </table>
                </div>
                <div className="error">
                </div>
            </div> 
        )
    }

    onRemoveUrl(index) {
        console.log("onRemoveUrl:"+index)
        this.state.data.splice(index,1)
        this.setState({data: this.props.data})
        console.log("state:", this.state)
     }


    addUrl(url) {
        console.log("adddUrl:"+url)
        var lastId = this.props.data[this.props.data.length-1].uid 
        this.props.data.push(UrlModel(lastId+1, url, "pending", 1551913200.0, VideoMetaData()))
        this.setState({data: this.props.data})
    }   
}

export default UrlTable ;
