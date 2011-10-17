/*****************************************************************************\

 jQuery "SOAP Client" plugin
 
 
	exemple d'utilisation
	
	var ws = new jQuery.SOAPClient({
						url 		: "_ws/connMoyen.php", 
						methode 	: "toto", 
						data		: {
										var1: data_0,
										var2 : "test"									
									 }, 
						async		: true, 
						success		: function(sr)
										{
											console.log(sr); // sr = l'ancien sr['return'] donc pas besoin d'ajouter ['return'] ;) 
										}, 
						error		: function(sr)
										{
										},
						spinner		: jQuery('#le bouton qu'on a cliquer pour lancer le soap par exemple') => sa va mettre licone loading a la place de ce bouton tant que le ws est en cours
						});
		ws.exec();	

\*****************************************************************************/

(function($) {
    jQuery.SOAPClient = function(options) {
			var settings = {
								requestType	: "soap1.1",
								methodType	: "POST",
								contentType	: "text/xml; charset=utf-8",
								async 		: true,
								spinner		: false,
								spinnerClone: false,
								success 	: function(){},
								error		: function(XMLHttpRequest, textStatus, errorThrown){throw XMLHttpRequest.responseText;}
							};
			jQuery.extend(settings,options);
			// this=this;
			this.settings=settings;
			this.exec = function(){
				if(this.settings.spinner){
					leDom = this.settings.spinner;
					this.settings.spinnerClone=jQuery(leDom).clone(true);
					jQuery(leDom).html('<center><img src="images/spinner.gif"/></center>');
				}
				if(this.settings.async)
					this._loadWsdl();
				else
					return this._loadWsdl();		
			}
			this._loadWsdl = function()
			{
				// load from cache?
				this.settings.wsdl = this_cacheWsdl[this.settings.url];
				if(this.settings.wsdl + "" != "" && this.settings.wsdl + "" != "undefined")
					return this._sendSoapRequest(this.settings);
				// get wsdl
				this.settings.xmlHttp = this._getXmlHttp();
				this.settings.xmlHttp.open("GET", this.settings.url + "?wsdl", this.settings.async);
				if(this.settings.async)
				{
					this.settings.xmlHttp.onreadystatechange = function()
					{
						if(this.settings.xmlHttp.readyState == 4)
							this._onLoadWsdl();
					}.bind(this)
				}
				this.settings.xmlHttp.send(null);
				if (!this.settings.async)
					return this._onLoadWsdl();
			}		
			this._onLoadWsdl = function()
			{
				this.settings.wsdl = this.settings.xmlHttp.responseXML;
				this_cacheWsdl[this.settings.url] = this.settings.wsdl;	// save a copy in cache
				return this._sendSoapRequest();
			}
			this._sendSoapRequest = function()
			{
				// get namespace
				this.settings.nameSpace = (this.settings.wsdl.documentElement.attributes["targetNamespace"] + "" == "undefined") ? this.settings.wsdl.documentElement.attributes.getNamedItem("targetNamespace").nodeValue : this.settings.wsdl.documentElement.attributes["targetNamespace"].value;
				// build SOAP request
					var oBuffer = new Array();		
					oBuffer.push("<?xml version=\"1.0\" encoding=\"utf-8\"?>");
					oBuffer.push("<soap:Envelope ");
					oBuffer.push("xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" ");
					//oBuffer.push("xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" ");
                    oBuffer.push("xmlns:xsd=\""+this.settings.nameSpace+"/xsd\" ");
					oBuffer.push("xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">");
					oBuffer.push("<soap:Body>");
					//oBuffer.push("<"+this.settings.methode+" xmlns=\""+this.settings.nameSpace+"\">");
                    oBuffer.push("<xsd:"+this.settings.methode+">");
					oBuffer.push(_serialize(this.settings.data));
					oBuffer.push("</xsd:"+this.settings.methode+">");
					oBuffer.push("</soap:Body>");
					oBuffer.push("</soap:Envelope>");			
					this.settings.requestData = oBuffer.join("");
					jQuery.ajax({
							type		: settings.methodType,
							cache		: false,
							async		: settings.async,
							url			: settings.url,
							data		: settings.requestData,
							contentType	: settings.contentType,
							dataType	: 'text',
							success		: function(o, statut,xmlHttp){
													this._onSendSoapRequest(this.settings.methode, this.settings.async, this.settings.success, this.settings.wsdl, xmlHttp);											
													if(this.settings.spinner){
														jQuery(this.settings.spinner).after(this.settings.spinnerClone).remove();
													}
											}.bind(this),
							error		: function(o){
													this.settings.error();
													if(this.settings.spinner){
														jQuery(this.settings.spinner).after(this.settings.spinnerClone).remove();
													}
											}.bind(this),
							beforeSend	: function(XMLHttpRequest){
												XMLHttpRequest.setRequestHeader("SOAPAction", this.settings.nameSpace + this.settings.methode);
												XMLHttpRequest.setRequestHeader("Content-Length",this.settings.requestData.length);
												XMLHttpRequest.setRequestHeader("Connection","close");
											}.bind(this)
					});
			}.bind(this)
		
		// private: wsdl cache
		this_cacheWsdl = new Array();

		this._onSendSoapRequest = function(method, async, callback, wsdl, req)
		{		 
			var o = null;
			var is_error=false;
			// On verifie que l'on a une reponce XML
			if(!req.responseXML)
			{
				if(async || callback)
						o = false;//new Error(500, "Le Web Service " + method+" ne repond pas");
					else
						throw new Error(500, "Le Web Service " + method+" ne repond pas");
			
			}
			else
			{
				// On recupere la reponse
				var nd = this._getElementsByTagName(req.responseXML, method + "Response");
				if(nd.length == 0)
				{
					if(req.responseXML.getElementsByTagName("faultcode").length > 0)
					{
						   is_error=true;
						if(async || callback)
							o = new Error(500, req.responseXML.getElementsByTagName("faultstring")[0].childNodes[0].nodeValue);
						else
							throw new Error(500, req.responseXML.getElementsByTagName("faultstring")[0].childNodes[0].nodeValue);
					}
				}
				else
					o = this._soapresult2object(nd[0], wsdl);
			}
			// En fonction du type de callback on retourne	
			if(o && o['return']!=null)
			retour = o['return'];
			else
			//retour=null;
            retour=o;
			if(callback)
			{	
				if(typeof(callback)=="function")
				{
					callback(retour, req.responseXML);
				}
				if(typeof(callback)=="object")
				{
					if(is_error)
						callback.error(retour, req.responseXML);
					else
						callback.success(retour, req.responseXML);
				}
			}
			if(!async)
				return retour;
		}
		this._soapresult2object = function(node, wsdl)
		{
			var wsdlTypes = this._getTypesFromWsdl(wsdl);
			return this._node2object(node, wsdlTypes);
		}
		this._node2object = function(node, wsdlTypes)
		{
			// null node
			if(node == null)
				return null;
			// text node
			if(node.nodeType == 3 || node.nodeType == 4)
				return this._extractValue(node, wsdlTypes);
			// leaf node
			if (node.childNodes.length == 1 && (node.childNodes[0].nodeType == 3 || node.childNodes[0].nodeType == 4))
				return this._node2object(node.childNodes[0], wsdlTypes);
			var isarray = this._getTypeFromWsdl(node.nodeName, wsdlTypes).toLowerCase().indexOf("arrayof") != -1;
			// object node
			if(!isarray)
			{
				var obj = null;
				if(node.hasChildNodes())
					obj = new Object();
				var j=0;
				for(var i = 0; i < node.childNodes.length; i++)
				{
					var p = this._node2object(node.childNodes[i], wsdlTypes);
					if (node.childNodes[i].nodeName=="item")
					{
						obj["item"+j] = p;
						j++;
					}
					else
					{
						if(node.childNodes[i].nodeName!="#text")
						obj[node.childNodes[i].nodeName] = p;
					}

				}
				return obj;
			}
			// list node
			else
			{
				// create node ref
				var l = new Array();
				for(var i = 0; i < node.childNodes.length; i++)
					l[l.length] = this._node2object(node.childNodes[i], wsdlTypes);
				return l;
			}
			return null;
		}
		this._extractValue = function(node, wsdlTypes)
		{
			var value = node.nodeValue;
			switch(this._getTypeFromWsdl(node.parentNode.nodeName, wsdlTypes).toLowerCase())
			{
				default:
				case "s:string":
					return (value != null) ? value + "" : "";
				case "s:boolean":
					return value + "" == "true";
				case "s:int":
				case "s:long":
					return (value != null) ? parseInt(value + "", 10) : 0;
				case "s:double":
					return (value != null) ? parseFloat(value + "") : 0;
				case "s:datetime":
					if(value == null)
						return null;
					else
					{
						value = value + "";
						value = value.substring(0, (value.lastIndexOf(".") == -1 ? value.length : value.lastIndexOf(".")));
						value = value.replace(/T/gi," ");
						value = value.replace(/-/gi,"/");
						var d = new Date();
						d.setTime(Date.parse(value));
						return d;
					}
			}
		}
		this._getTypesFromWsdl = function(wsdl)
		{
			var wsdlTypes = new Array();
			// IE
			var ell = wsdl.getElementsByTagName("s:element");
			var useNamedItem = true;
			// MOZ
			if(ell.length == 0)
			{
				ell = wsdl.getElementsByTagName("element");
				useNamedItem = false;
			}
			for(var i = 0; i < ell.length; i++)
			{
				if(useNamedItem)
				{
					if(ell[i].attributes.getNamedItem("name") != null && ell[i].attributes.getNamedItem("type") != null)
						wsdlTypes[ell[i].attributes.getNamedItem("name").nodeValue] = ell[i].attributes.getNamedItem("type").nodeValue;
				}
				else
				{
					if(ell[i].attributes["name"] != null && ell[i].attributes["type"] != null)
						wsdlTypes[ell[i].attributes["name"].value] = ell[i].attributes["type"].value;
				}
			}
			return wsdlTypes;
		}
		this._getTypeFromWsdl = function(elementname, wsdlTypes)
		{
			var type = wsdlTypes[elementname] + "";
			return (type == "undefined") ? "" : type;
		}
		// private: utils
		this._getElementsByTagName = function(el, tagName)
		{
			try
			{
				// Ajout pour Internet explorer 7
				el.setProperty("SelectionLanguage", "XPath");
				// trying to get node omitting any namespaces (latest versions of MSXML.XMLDocument)
				var tag = el.selectNodes(".//*[local-name()=\""+ tagName +"\"]");
				return tag;
			}
			catch (ex) {}
			// old XML parser support
			var test = el.getElementsByTagName(tagName);
			// Ajout pour firefox 3
			if (test.length == 0) test = el.getElementsByTagName("ns4:"+tagName);
			return test;
		}
		// private: xmlhttp factory
		this._getXmlHttp = function()
		{
			try
			{
				if(window.XMLHttpRequest)
				{
					var req = new XMLHttpRequest();
					// some versions of Moz do not support the readyState property and the onreadystate event so we patch it!
					if(req.readyState == null)
					{
						req.readyState = 1;
						req.addEventListener("load",
											function()
											{
												req.readyState = 4;
												if(typeof req.onreadystatechange == "function")
													req.onreadystatechange();
											},
											false);
					}
					return req;
				}
				if(window.ActiveXObject)
					return new ActiveXObject(this._getXmlHttpProgID());
			}
			catch (ex) {}
			throw new Error("Your browser does not support XmlHttp objects");
		}
		
		this._getXmlHttpProgID = function()
		{
			if(this._getXmlHttpProgID.progid)
				return this._getXmlHttpProgID.progid;
			var progids = ["Msxml2.XMLHTTP.5.0", "Msxml2.XMLHTTP.4.0", "MSXML2.XMLHTTP.3.0", "MSXML2.XMLHTTP", "Microsoft.XMLHTTP"];
			var o;
			for(var i = 0; i < progids.length; i++)
			{
				try
				{
					o = new ActiveXObject(progids[i]);
					return this._getXmlHttpProgID.progid = progids[i];
				}
				catch (ex) {};
			}
			throw new Error("Could not find an installed XML parser");
		}



		_serialize = function(o)
		{
			var s = "";
			switch(typeof(o))
			{
				case "string":
					s += o.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); break;
				case "number":
				case "boolean":
					s += o.toString(); break;
				case "object":
					// Date
					if(o.constructor.toString().indexOf("function Date()") > -1)
					{

						var year = o.getFullYear().toString();
						var month = (o.getMonth() + 1).toString(); month = (month.length == 1) ? "0" + month : month;
						var date = o.getDate().toString(); date = (date.length == 1) ? "0" + date : date;
						var hours = o.getHours().toString(); hours = (hours.length == 1) ? "0" + hours : hours;
						var minutes = o.getMinutes().toString(); minutes = (minutes.length == 1) ? "0" + minutes : minutes;
						var seconds = o.getSeconds().toString(); seconds = (seconds.length == 1) ? "0" + seconds : seconds;
						var milliseconds = o.getMilliseconds().toString();
						var tzminutes = Math.abs(o.getTimezoneOffset());
						var tzhours = 0;
						while(tzminutes >= 60)
						{
							tzhours++;
							tzminutes -= 60;
						}
						tzminutes = (tzminutes.toString().length == 1) ? "0" + tzminutes.toString() : tzminutes.toString();
						tzhours = (tzhours.toString().length == 1) ? "0" + tzhours.toString() : tzhours.toString();
						var timezone = ((o.getTimezoneOffset() < 0) ? "+" : "-") + tzhours + ":" + tzminutes;
						s += year + "-" + month + "-" + date + "T" + hours + ":" + minutes + ":" + seconds + "." + milliseconds + timezone;
					}
					// Array
					else if(o.constructor.toString().indexOf("function Array()") > -1)
					{			
						o.each(function(item, index){
						   if(!isNaN(index))   // linear array
								{
									var type = typeof(item);
									switch(type)
									{
										case "String":
											type = "string"; break;
										case "Number":
											type = "int"; break;
										case "Boolean":
											type = "bool"; break;
										case "Date":
											type = "DateTime"; break;
									}
									//s += "<" + type + ">" + _serialize(item) + "</" + type + ">"
                                    s += "<xsd:" + type + ">" + _serialize(item) + "</xsd:" + type + ">"
								}
								else    // associative array
									//s += "<" + index + ">" + _serialize(item) + "</" + index + ">"
                                    s += "<xsd:" + index + ">" + _serialize(item) + "</xsd:" + index + ">"
						});
					}
					// Object or custom function
					else
						for(var p in o)
							//s += "<" + p + ">" + _serialize(o[p]) + "</" + p + ">";
                            s += "<xsd:" + p + ">" + _serialize(o[p]) + "</xsd:" + p + ">";
					break;
				default:
					break; // throw new Error(500, "this: type '" + typeof(o) + "' is not supported");
			}
			return s;
		}
}
})(jQuery);