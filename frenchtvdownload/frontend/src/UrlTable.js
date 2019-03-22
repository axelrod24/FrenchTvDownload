import React, { Component } from 'react';
import {UrlModel, VideoMetaData} from "./model.js"

const Item = ({classname, value, style}) => <td className={classname} style={style}>{value}</td>
const Button = ({classname, value, style, onClick}) => <button className={classname} style={style} onClick={onClick}>{value}</button>
const ButtonItem = ({classname, value, style, onClick}) => <Item className={classname} style={style} value={<button> onClick={onClick}>{value}</button>} />


class Row extends Component {
    constructor(props) {
        super(props) ;
        this.state = {
            status: this.props.data.status
        }

        this.onDownloadVideo = this.onDownloadVideo.bind(this)
        this.onCancelDownload = this.onCancelDownload.bind(this)
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
                statusText = "..."
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

            return ( 
            <tr>
                <Item value={this.props.data.uid} />
                <Item classname="url" value={this.props.data.url} />
                <Item value={this.props.data.timestamp}/>
                <Item value={statusText} style={{background: statusBgColor}}/>
                <td>
                    {(this.state.status==="downloading") ? 
                        <Button value="Cancel" onClick={this.onCancelDownload}/> : <Button value="Remove" onClick={() => this.props.onRemoveUrl(this.props.index)}/>}
                    {(this.state.status==="pending") && <Button value="Download" onClick={this.onDownloadVideo}/>}
                </td>
            </tr>
        )
    }

    onDownloadVideo() {
        console.log("onDownloadVideo:",this.props.index)
    }

    onCancelDownload() {
        console.log("onCancelDownload:",this.props.index)
    }
}



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
                        <caption>List of Url</caption>
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
                            {this.state.data.map((data, index) => <Row key={data.uid} data={data} index={index} onRemoveUrl={this.onRemoveUrl}/>)}
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
