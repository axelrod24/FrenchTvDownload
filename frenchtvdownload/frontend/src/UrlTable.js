import React, { Component } from 'react';
import AddUrlButton from './Button.js';


const Item = ({classname, value, style}) => <td className={classname} style={style}>{value}</td>
const Button = ({classname, value, style, onClick}) => <button className={classname} style={style} onClick={onClick}>{value}</button>

class Row extends Component {
    constructor(props) {
        super(props) ;
        this.state = {
            status: this.props.data.status
        }
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
                <td><Button value="Remove" onClick={() => this.props.onRemoveUrl(this.props.index)}/></td>
            </tr>
        )
    }

    onDownloadVideo() {

    }

    onCancelDownload() {

    }
}

class UrlTable extends Component {
    constructor(props) {
        super(props) ;
        this.state = { 
            data: this.props.data
        }

        this.onRemoveUrl = this.onRemoveUrl.bind(this)
    }

    render() {
        return (
            <div>
                <div className="editor">
                    <label htmlFor="url" style={{width: '80%'}}>Url :
                        <input id="url" type="text" style={{width: '80%'}}/>
                        <AddUrlButton />
                    </label>
                </div>
        
                <div className="people">
                    <table>
                        <caption>List of Url</caption>
                        <thead>
                            <tr>
                                <th>Id</th>
                                <th>Url</th>
                                <th>Status</th>
                                <th>Timestamp</th>
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


    onAddUrl() {

    }


}

export default UrlTable ;
