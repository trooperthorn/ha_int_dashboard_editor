function t(t,e,s,i){var r,o=arguments.length,a=o<3?e:null===i?i=Object.getOwnPropertyDescriptor(e,s):i;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)a=Reflect.decorate(t,e,s,i);else for(var n=t.length-1;n>=0;n--)(r=t[n])&&(a=(o<3?r(a):o>3?r(e,s,a):r(e,s))||a);return o>3&&a&&Object.defineProperty(e,s,a),a}"function"==typeof SuppressedError&&SuppressedError;
/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const e=globalThis,s=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,i=Symbol(),r=new WeakMap;let o=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==i)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(s&&void 0===t){const s=void 0!==e&&1===e.length;s&&(t=r.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&r.set(e,t))}return t}toString(){return this.cssText}};const a=s?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return(t=>new o("string"==typeof t?t:t+"",void 0,i))(e)})(t):t,{is:n,defineProperty:d,getOwnPropertyDescriptor:h,getOwnPropertyNames:l,getOwnPropertySymbols:c,getPrototypeOf:p}=Object,u=globalThis,_=u.trustedTypes,f=_?_.emptyScript:"",$=u.reactiveElementPolyfillSupport,g=(t,e)=>t,b={toAttribute(t,e){switch(e){case Boolean:t=t?f:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},m=(t,e)=>!n(t,e),v={attribute:!0,type:String,converter:b,reflect:!1,useDefault:!1,hasChanged:m};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */Symbol.metadata??=Symbol("metadata"),u.litPropertyMetadata??=new WeakMap;let y=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=v){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const s=Symbol(),i=this.getPropertyDescriptor(t,s,e);void 0!==i&&d(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){const{get:i,set:r}=h(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:i,set(e){const o=i?.call(this);r?.call(this,e),this.requestUpdate(t,o,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??v}static _$Ei(){if(this.hasOwnProperty(g("elementProperties")))return;const t=p(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(g("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(g("properties"))){const t=this.properties,e=[...l(t),...c(t)];for(const s of e)this.createProperty(s,t[s])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,s]of e)this.elementProperties.set(t,s)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const s=this._$Eu(t,e);void 0!==s&&this._$Eh.set(s,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(a(t))}else void 0!==t&&e.push(a(t));return e}static _$Eu(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,i)=>{if(s)t.adoptedStyleSheets=i.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const s of i){const i=document.createElement("style"),r=e.litNonce;void 0!==r&&i.setAttribute("nonce",r),i.textContent=s.cssText,t.appendChild(i)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){const s=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,s);if(void 0!==i&&!0===s.reflect){const r=(void 0!==s.converter?.toAttribute?s.converter:b).toAttribute(e,s.type);this._$Em=t,null==r?this.removeAttribute(i):this.setAttribute(i,r),this._$Em=null}}_$AK(t,e){const s=this.constructor,i=s._$Eh.get(t);if(void 0!==i&&this._$Em!==i){const t=s.getPropertyOptions(i),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:b;this._$Em=i;const o=r.fromAttribute(e,t.type);this[i]=o??this._$Ej?.get(i)??o,this._$Em=null}}requestUpdate(t,e,s,i=!1,r){if(void 0!==t){const o=this.constructor;if(!1===i&&(r=this[t]),s??=o.getPropertyOptions(t),!((s.hasChanged??m)(r,e)||s.useDefault&&s.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(o._$Eu(t,s))))return;this.C(t,e,s)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:i,wrapped:r},o){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,o??e??this[t]),!0!==r||void 0!==o)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),!0===i&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,s]of t){const{wrapped:t}=s,i=this[e];!0!==t||this._$AL.has(e)||void 0===i||this.C(e,void 0,s,i)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};y.elementStyles=[],y.shadowRootOptions={mode:"open"},y[g("elementProperties")]=new Map,y[g("finalized")]=new Map,$?.({ReactiveElement:y}),(u.reactiveElementVersions??=[]).push("2.1.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const A=globalThis,w=t=>t,x=A.trustedTypes,S=x?x.createPolicy("lit-html",{createHTML:t=>t}):void 0,E="$lit$",C=`lit$${Math.random().toFixed(9).slice(2)}$`,k="?"+C,P=`<${k}>`,O=document,M=()=>O.createComment(""),N=t=>null===t||"object"!=typeof t&&"function"!=typeof t,U=Array.isArray,R="[ \t\n\f\r]",H=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,T=/-->/g,D=/>/g,z=RegExp(`>|${R}(?:([^\\s"'>=/]+)(${R}*=${R}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),j=/'/g,W=/"/g,L=/^(?:script|style|textarea|title)$/i,q=(t=>(e,...s)=>({_$litType$:t,strings:e,values:s}))(1),I=Symbol.for("lit-noChange"),B=Symbol.for("lit-nothing"),V=new WeakMap,F=O.createTreeWalker(O,129);function Y(t,e){if(!U(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==S?S.createHTML(e):e}const J=(t,e)=>{const s=t.length-1,i=[];let r,o=2===e?"<svg>":3===e?"<math>":"",a=H;for(let e=0;e<s;e++){const s=t[e];let n,d,h=-1,l=0;for(;l<s.length&&(a.lastIndex=l,d=a.exec(s),null!==d);)l=a.lastIndex,a===H?"!--"===d[1]?a=T:void 0!==d[1]?a=D:void 0!==d[2]?(L.test(d[2])&&(r=RegExp("</"+d[2],"g")),a=z):void 0!==d[3]&&(a=z):a===z?">"===d[0]?(a=r??H,h=-1):void 0===d[1]?h=-2:(h=a.lastIndex-d[2].length,n=d[1],a=void 0===d[3]?z:'"'===d[3]?W:j):a===W||a===j?a=z:a===T||a===D?a=H:(a=z,r=void 0);const c=a===z&&t[e+1].startsWith("/>")?" ":"";o+=a===H?s+P:h>=0?(i.push(n),s.slice(0,h)+E+s.slice(h)+C+c):s+C+(-2===h?e:c)}return[Y(t,o+(t[s]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),i]};class K{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let r=0,o=0;const a=t.length-1,n=this.parts,[d,h]=J(t,e);if(this.el=K.createElement(d,s),F.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(i=F.nextNode())&&n.length<a;){if(1===i.nodeType){if(i.hasAttributes())for(const t of i.getAttributeNames())if(t.endsWith(E)){const e=h[o++],s=i.getAttribute(t).split(C),a=/([.?@])?(.*)/.exec(e);n.push({type:1,index:r,name:a[2],strings:s,ctor:"."===a[1]?tt:"?"===a[1]?et:"@"===a[1]?st:X}),i.removeAttribute(t)}else t.startsWith(C)&&(n.push({type:6,index:r}),i.removeAttribute(t));if(L.test(i.tagName)){const t=i.textContent.split(C),e=t.length-1;if(e>0){i.textContent=x?x.emptyScript:"";for(let s=0;s<e;s++)i.append(t[s],M()),F.nextNode(),n.push({type:2,index:++r});i.append(t[e],M())}}}else if(8===i.nodeType)if(i.data===k)n.push({type:2,index:r});else{let t=-1;for(;-1!==(t=i.data.indexOf(C,t+1));)n.push({type:7,index:r}),t+=C.length-1}r++}}static createElement(t,e){const s=O.createElement("template");return s.innerHTML=t,s}}function Z(t,e,s=t,i){if(e===I)return e;let r=void 0!==i?s._$Co?.[i]:s._$Cl;const o=N(e)?void 0:e._$litDirective$;return r?.constructor!==o&&(r?._$AO?.(!1),void 0===o?r=void 0:(r=new o(t),r._$AT(t,s,i)),void 0!==i?(s._$Co??=[])[i]=r:s._$Cl=r),void 0!==r&&(e=Z(t,r._$AS(t,e.values),r,i)),e}class G{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:s}=this._$AD,i=(t?.creationScope??O).importNode(e,!0);F.currentNode=i;let r=F.nextNode(),o=0,a=0,n=s[0];for(;void 0!==n;){if(o===n.index){let e;2===n.type?e=new Q(r,r.nextSibling,this,t):1===n.type?e=new n.ctor(r,n.name,n.strings,this,t):6===n.type&&(e=new it(r,this,t)),this._$AV.push(e),n=s[++a]}o!==n?.index&&(r=F.nextNode(),o++)}return F.currentNode=O,i}p(t){let e=0;for(const s of this._$AV)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}class Q{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,i){this.type=2,this._$AH=B,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Z(this,t,e),N(t)?t===B||null==t||""===t?(this._$AH!==B&&this._$AR(),this._$AH=B):t!==this._$AH&&t!==I&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>U(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==B&&N(this._$AH)?this._$AA.nextSibling.data=t:this.T(O.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:s}=t,i="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=K.createElement(Y(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(e);else{const t=new G(i,this),s=t.u(this.options);t.p(e),this.T(s),this._$AH=t}}_$AC(t){let e=V.get(t.strings);return void 0===e&&V.set(t.strings,e=new K(t)),e}k(t){U(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,i=0;for(const r of t)i===e.length?e.push(s=new Q(this.O(M()),this.O(M()),this,this.options)):s=e[i],s._$AI(r),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=w(t).nextSibling;w(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class X{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,i,r){this.type=1,this._$AH=B,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=r,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=B}_$AI(t,e=this,s,i){const r=this.strings;let o=!1;if(void 0===r)t=Z(this,t,e,0),o=!N(t)||t!==this._$AH&&t!==I,o&&(this._$AH=t);else{const i=t;let a,n;for(t=r[0],a=0;a<r.length-1;a++)n=Z(this,i[s+a],e,a),n===I&&(n=this._$AH[a]),o||=!N(n)||n!==this._$AH[a],n===B?t=B:t!==B&&(t+=(n??"")+r[a+1]),this._$AH[a]=n}o&&!i&&this.j(t)}j(t){t===B?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class tt extends X{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===B?void 0:t}}class et extends X{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==B)}}class st extends X{constructor(t,e,s,i,r){super(t,e,s,i,r),this.type=5}_$AI(t,e=this){if((t=Z(this,t,e,0)??B)===I)return;const s=this._$AH,i=t===B&&s!==B||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==B&&(s===B||i);i&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class it{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){Z(this,t)}}const rt=A.litHtmlPolyfillSupport;rt?.(K,Q),(A.litHtmlVersions??=[]).push("3.3.3");const ot=globalThis;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */class at extends y{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,s)=>{const i=s?.renderBefore??e;let r=i._$litPart$;if(void 0===r){const t=s?.renderBefore??null;i._$litPart$=r=new Q(e.insertBefore(M(),t),t,void 0,s??{})}return r._$AI(t),r})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return I}}at._$litElement$=!0,at.finalized=!0,ot.litElementHydrateSupport?.({LitElement:at});const nt=ot.litElementPolyfillSupport;nt?.({LitElement:at}),(ot.litElementVersions??=[]).push("4.2.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const dt={attribute:!0,type:String,converter:b,reflect:!1,hasChanged:m},ht=(t=dt,e,s)=>{const{kind:i,metadata:r}=s;let o=globalThis.litPropertyMetadata.get(r);if(void 0===o&&globalThis.litPropertyMetadata.set(r,o=new Map),"setter"===i&&((t=Object.create(t)).wrapped=!0),o.set(s.name,t),"accessor"===i){const{name:i}=s;return{set(s){const r=e.get.call(this);e.set.call(this,s),this.requestUpdate(i,r,t,!0,s)},init(e){return void 0!==e&&this.C(i,void 0,t,e),e}}}if("setter"===i){const{name:i}=s;return function(s){const r=this[i];e.call(this,s),this.requestUpdate(i,r,t,!0,s)}}throw Error("Unsupported decorator location: "+i)};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function lt(t){return(e,s)=>"object"==typeof s?ht(t,e,s):((t,e,s)=>{const i=e.hasOwnProperty(s);return e.constructor.createProperty(s,t),i?Object.getOwnPropertyDescriptor(e,s):void 0})(t,e,s)}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function ct(t){return lt({...t,state:!0,attribute:!1})}const pt=t=>t.callWS({type:"dashboard_editor/config/get"}),ut=t=>t.callWS({type:"lovelace/dashboards/list"}),_t=(t,e)=>t.callWS({type:"lovelace/dashboards/delete",dashboard_id:e}),ft=(t,e)=>t.callWS({type:"lovelace/config",url_path:e,force:!0}),$t=t=>{history.pushState(null,"",t),window.dispatchEvent(new CustomEvent("location-changed",{detail:{replace:!1}}))},gt={set:"changed",add:"added",delete:"removed",insert:"card added",remove:"card removed",replace:"replaced",reorder:"reordered",resize:"list rebuilt",include_dropped:"include replaced by inline value"};let bt=class extends at{constructor(){super(...arguments),this._listing=null,this._scratch=new Map,this._plans=new Map,this._busy=null,this._error=null,this._message=null,this._config=null,this._drafts=[],this._restartNeeded=!1}connectedCallback(){super.connectedCallback(),this._refresh()}async _refresh(){this._error=null;try{const[e,s,i]=await Promise.all([(t=this.hass,t.callWS({type:"dashboard_editor/list"})),ut(this.hass),pt(this.hass)]);this._listing=e;const r=new Map;for(const t of s){const s=e.dashboards.find(e=>e.scratch_url_path===t.url_path);s&&r.set(s.id,t)}this._scratch=r,this._config=i,this._drafts=i.entries.map(t=>({...t,create_file:!1}))}catch(t){this._error=mt(t)}var t}async _run(t,e){this._busy=t,this._error=null,this._message=null;try{await e()}catch(t){this._error=mt(t)}finally{this._busy=null}}_open(t){return this._run(t.id,async()=>{const e=await(s=this.hass,i=t.id,s.callWS({type:"dashboard_editor/resolve",dashboard_id:i}));var s,i;let r=this._scratch.get(t.id);r||(r=await((t,e,s,i)=>t.callWS({type:"lovelace/dashboards/create",url_path:e,title:s,icon:i??"mdi:pencil-box-outline",show_in_sidebar:!1,require_admin:!0}))(this.hass,t.scratch_url_path,`Editing ${t.title}`,t.icon)),await((t,e,s)=>t.callWS({type:"lovelace/config/save",url_path:e,config:s}))(this.hass,t.scratch_url_path,e.config),await this._refresh(),$t(`/${t.scratch_url_path}/0?edit=1`)})}_preview(t){return this._run(t.id,async()=>{const e=await ft(this.hass,t.scratch_url_path),s=await((t,e,s)=>t.callWS({type:"dashboard_editor/plan",dashboard_id:e,config:s}))(this.hass,t.id,e);this._plans=new Map(this._plans).set(t.id,s)})}_commit(t){return this._run(t.id,async()=>{const e=await ft(this.hass,t.scratch_url_path),s=await((t,e,s)=>t.callWS({type:"dashboard_editor/commit",dashboard_id:e,config:s}))(this.hass,t.id,e);this._plans=new Map(this._plans).set(t.id,s),await ft(this.hass,t.url_path);const i=this._scratch.get(t.id);i&&0===s.blocked.length&&await _t(this.hass,i.id),this._message=0===s.written.length?`Nothing to write for ${t.title}; the files already match.`:`Wrote ${s.written.join(", ")} for ${t.title}. Backup in ${s.backup}. Open the dashboard and choose Refresh if it still shows the old version.`,await this._refresh()})}_discard(t){return this._run(t.id,async()=>{const e=this._scratch.get(t.id);e&&await _t(this.hass,e.id);const s=new Map(this._plans);s.delete(t.id),this._plans=s,await this._refresh()})}_renderDashboards(){const t=this._listing;return t?0===t.dashboards.length?q`<p class="muted">
        No YAML-mode dashboards are registered. Add one in the block below and restart Home Assistant.
      </p>`:q`
      <table>
        <tr>
          <th>Dashboard</th>
          <th>File</th>
          <th>State</th>
          <th></th>
        </tr>
        ${t.dashboards.map(t=>this._renderRow(t))}
      </table>
    `:q`<p class="muted">Loading…</p>`}_renderRow(t){const e=this._scratch.get(t.id),s=this._busy===t.id,i=this._plans.get(t.id);return q`
      <tr>
        <td>
          <strong>${t.title}</strong><br />
          <span class="muted">/${t.url_path}</span>
        </td>
        <td>
          <code>${t.file}</code>
          ${t.includes.length?q`<br /><span class="muted">${t.includes.length} included file${1===t.includes.length?"":"s"}</span>`:B}
          ${t.problem?q`<div class="alert">${t.problem}</div>`:B}
        </td>
        <td>
          ${e?q`<span class="pill open">editing</span><br /><span class="muted">/${t.scratch_url_path}</span>`:q`<span class="pill">on disk</span>`}
        </td>
        <td>
          <div class="actions">
            ${e?q`
                  <button ?disabled=${s} @click=${()=>$t(`/${t.scratch_url_path}/0?edit=1`)}>
                    Continue editing
                  </button>
                  <button ?disabled=${s} @click=${()=>this._preview(t)}>Preview changes</button>
                  <button class="primary" ?disabled=${s} @click=${()=>this._commit(t)}>Commit</button>
                  <button class="danger" ?disabled=${s} @click=${()=>this._discard(t)}>Discard</button>
                `:q`
                  <button class="primary" ?disabled=${s||!t.supported} @click=${()=>this._open(t)}>
                    ${s?"Opening…":"Open in editor"}
                  </button>
                `}
          </div>
          ${i?this._renderPlan(i):B}
        </td>
      </tr>
    `}_renderPlan(t){const e=t.written;return q`
      <div class="plan">
        ${e?q`<strong>${e.length?`Written: ${e.join(", ")}`:"Nothing was written."}</strong>`:t.changes.length?q`<strong>${t.files.length} file${1===t.files.length?"":"s"} will change</strong>`:q`<strong>No changes.</strong>`}
        ${t.changes.length?q`<ul>
              ${t.changes.map(t=>q`<li><code>${t.file}</code> ${t.path}: ${gt[t.kind]??t.kind}${t.detail?` (${t.detail})`:""}</li>`)}
            </ul>`:B}
        ${t.warnings.map(t=>q`<div class="notice">${t}</div>`)}
        ${t.blocked.length?q`<div class="alert">Not written, edit the file directly:\n${t.blocked.join("\n")}</div>`:B}
      </div>
    `}_draftChanged(t,e){this._drafts=this._drafts.map((s,i)=>i===t?{...s,...e}:s)}_addDraft(){this._drafts=[...this._drafts,{url_path:"",title:"",icon:"mdi:view-dashboard",show_in_sidebar:!0,require_admin:!1,filename:"dashboards/",create_file:!0,isNew:!0}]}_saveDraft(t){const e=this._drafts[t];return this._run(`cfg-${t}`,async()=>{var t,s;await(t=this.hass,s={url_path:e.url_path.trim(),title:e.title||null,icon:e.icon||null,show_in_sidebar:e.show_in_sidebar??!0,require_admin:e.require_admin??!1,filename:(e.filename??"").trim(),create_file:e.create_file},t.callWS({type:"dashboard_editor/config/set",...s})),this._restartNeeded=!0,await this._refresh()})}_removeDraft(t){const e=this._drafts[t];if(e.isNew)this._drafts=this._drafts.filter((e,s)=>s!==t);else if(window.confirm(`Remove ${e.url_path} from the dashboards block? The file stays on disk.`))return this._run(`cfg-${t}`,async()=>{var t,s;await(t=this.hass,s=e.url_path,t.callWS({type:"dashboard_editor/config/remove",url_path:s})),this._restartNeeded=!0,await this._refresh()})}_renderConfig(){const t=this._config;return t?q`
      <p class="muted">
        The <code>lovelace: dashboards:</code> block in <code>${t.file}</code>.
        ${t.mode?q`Top-level mode <code>${t.mode}</code>.`:B}
        Resources stay in ${this._listing?.resource_mode??"storage"} mode and are managed under Settings, Dashboards.
        Home Assistant reads this block at startup, so every change here needs a restart.
      </p>
      ${t.problem?q`<div class="alert">${t.problem}</div>`:B}
      ${this._restartNeeded?q`<div class="notice">Restart Home Assistant to register the changed dashboards.</div>`:B}
      <table>
        <tr>
          <th style="width:18%">URL</th>
          <th style="width:18%">Title</th>
          <th style="width:16%">Icon</th>
          <th style="width:24%">File</th>
          <th>Flags</th>
          <th></th>
        </tr>
        ${this._drafts.map((t,e)=>this._renderDraft(t,e))}
      </table>
      <div class="actions" style="margin-top:10px">
        <button ?disabled=${!t.writable} @click=${()=>this._addDraft()}>Add YAML dashboard</button>
      </div>
    `:B}_renderDraft(t,e){const s=this._busy===`cfg-${e}`,i=this._config?.writable??!1;return q`
      <tr>
        <td>
          ${t.isNew?q`<input type="text" placeholder="garage-dashboard" .value=${t.url_path} @input=${t=>this._draftChanged(e,{url_path:t.target.value})} />`:q`<code>${t.url_path}</code>`}
        </td>
        <td><input type="text" .value=${t.title??""} @input=${t=>this._draftChanged(e,{title:t.target.value})} /></td>
        <td><input type="text" .value=${t.icon??""} @input=${t=>this._draftChanged(e,{icon:t.target.value})} /></td>
        <td>
          <input type="text" .value=${t.filename??""} @input=${t=>this._draftChanged(e,{filename:t.target.value})} />
          <label class="inline"><input type="checkbox" .checked=${t.create_file} @change=${t=>this._draftChanged(e,{create_file:t.target.checked})} /> create if missing</label>
        </td>
        <td>
          <label class="inline"><input type="checkbox" .checked=${t.show_in_sidebar??!0} @change=${t=>this._draftChanged(e,{show_in_sidebar:t.target.checked})} /> sidebar</label><br />
          <label class="inline"><input type="checkbox" .checked=${t.require_admin??!1} @change=${t=>this._draftChanged(e,{require_admin:t.target.checked})} /> admin only</label>
        </td>
        <td>
          <div class="actions">
            <button class="primary" ?disabled=${s||!i} @click=${()=>this._saveDraft(e)}>Save</button>
            <button class="danger" ?disabled=${s||!i} @click=${()=>this._removeDraft(e)}>${t.isNew?"Cancel":"Remove"}</button>
          </div>
        </td>
      </tr>
    `}render(){return q`
      <div class="page">
        <h1>Dashboard editor</h1>
        <p class="muted">
          Open a YAML-mode dashboard in Home Assistant's own editor, then commit the result back into the
          files it was assembled from, <code>!include</code> fragments included. A commit backs up every file
          it rewrites under <code>.storage/dashboard_editor/backups</code>.
        </p>
        ${this._error?q`<div class="alert">${this._error}</div>`:B}
        ${this._message?q`<div class="notice">${this._message}</div>`:B}
        <h2>YAML dashboards</h2>
        <div class="card">${this._renderDashboards()}</div>
        <h2>Dashboards block</h2>
        <div class="card">${this._renderConfig()}</div>
      </div>
    `}};function mt(t){const e=t;return e?.message??e?.code??String(t)}bt.styles=((t,...e)=>{const s=1===t.length?t[0]:e.reduce((e,s,i)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[i+1],t[0]);return new o(s,t,i)})`
    :host {
      display: block;
      background: var(--primary-background-color);
      color: var(--primary-text-color);
      min-height: 100vh;
    }
    .page {
      max-width: 1100px;
      margin: 0 auto;
      padding: 20px clamp(14px, 2vw, 24px) 40px;
    }
    h1 {
      font-size: 22px;
      font-weight: 500;
      margin: 0 0 4px;
    }
    h2 {
      font-size: 16px;
      font-weight: 500;
      margin: 28px 0 10px;
    }
    .muted {
      color: var(--secondary-text-color);
      font-size: 13px;
    }
    .card {
      background: var(--card-background-color, #fff);
      border-radius: var(--ha-card-border-radius, 12px);
      border: 1px solid var(--divider-color);
      padding: 14px 16px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }
    th {
      text-align: left;
      font-weight: 500;
      color: var(--secondary-text-color);
      font-size: 12px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      padding: 6px 8px;
      border-bottom: 1px solid var(--divider-color);
    }
    td {
      padding: 8px;
      border-bottom: 1px solid var(--divider-color);
      vertical-align: top;
    }
    tr:last-child td {
      border-bottom: 0;
    }
    code {
      font-family: var(--ha-font-family-code, monospace);
      font-size: 12.5px;
    }
    .actions {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }
    button {
      font: inherit;
      font-size: 13px;
      padding: 6px 12px;
      border-radius: 8px;
      border: 1px solid var(--divider-color);
      background: var(--card-background-color, #fff);
      color: var(--primary-text-color);
      cursor: pointer;
    }
    button.primary {
      background: var(--primary-color);
      color: var(--text-primary-color, #fff);
      border-color: var(--primary-color);
    }
    button.danger {
      color: var(--error-color);
    }
    button:disabled {
      opacity: 0.5;
      cursor: default;
    }
    .pill {
      display: inline-block;
      font-size: 12px;
      padding: 1px 8px;
      border-radius: 10px;
      background: rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.06);
    }
    .pill.open {
      background: var(--primary-color);
      color: var(--text-primary-color, #fff);
    }
    .alert {
      border-left: 3px solid var(--error-color);
      padding: 8px 12px;
      margin: 10px 0;
      background: rgba(var(--rgb-error-color, 219, 68, 55), 0.08);
      font-size: 13px;
      white-space: pre-wrap;
    }
    .notice {
      border-left: 3px solid var(--warning-color, #ffa600);
      padding: 8px 12px;
      margin: 10px 0;
      background: rgba(var(--rgb-warning-color, 255, 166, 0), 0.08);
      font-size: 13px;
    }
    .plan {
      margin-top: 12px;
      border-top: 1px solid var(--divider-color);
      padding-top: 10px;
    }
    .plan ul {
      margin: 6px 0 0;
      padding-left: 18px;
      font-size: 13px;
    }
    input[type="text"],
    select {
      font: inherit;
      font-size: 13px;
      padding: 4px 6px;
      border-radius: 6px;
      border: 1px solid var(--divider-color);
      background: var(--card-background-color, #fff);
      color: var(--primary-text-color);
      width: 100%;
      box-sizing: border-box;
    }
    label.inline {
      display: inline-flex;
      gap: 4px;
      align-items: center;
      font-size: 13px;
      white-space: nowrap;
    }
  `,t([lt({attribute:!1})],bt.prototype,"hass",void 0),t([ct()],bt.prototype,"_listing",void 0),t([ct()],bt.prototype,"_scratch",void 0),t([ct()],bt.prototype,"_plans",void 0),t([ct()],bt.prototype,"_busy",void 0),t([ct()],bt.prototype,"_error",void 0),t([ct()],bt.prototype,"_message",void 0),t([ct()],bt.prototype,"_config",void 0),t([ct()],bt.prototype,"_drafts",void 0),t([ct()],bt.prototype,"_restartNeeded",void 0),bt=t([(t=>(e,s)=>{void 0!==s?s.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)})("dashboard-editor-panel")],bt);export{bt as DashboardEditorPanel};
