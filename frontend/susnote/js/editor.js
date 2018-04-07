$(document).ready(function(){

  initial_data();
});

function Ajax(obj){
  this.method = obj.method || '';
  this.url = obj.url || '';
  this.callback = obj.callback || '';
  this.data = obj.data || '';
};
Ajax.prototype.send = function(method,url,callback,data){
  var method = method || this.method;
  var data = data || this.data;
  var url = url || this.url;
  var callback = callback || this.callback;
  var xhr = new XMLHttpRequest();//新建ajax请求，不兼容IE7以下
  xhr.onreadystatechange = function(){//注册回调函数
    if(xhr.readyState === 4){
      if(xhr.status === 200)
        callback(xhr.responseText);
      else
      	alert('Server Error');
    }
  }
  if(method === 'get'){//如果是get方法，需要把data中的数据转化作为url传递给服务器
    if(typeof data === 'object'){
      var data_send = '?';
      for(var key in data){
        data_send+=key+'='+data[key];
        data_send+='&';
      }
      data_send = data_send.slice(0,-1);
    }
    xhr.open(method,url+data_send,true);
    xhr.send(null);
  }else if(method === 'post' || method === 'put'){//如果是post，需要在头中添加content-type说明
      xhr.open(method,url,true);
      xhr.setRequestHeader('Content-Type','application/json');
      xhr.send(JSON.stringify(data));//发送的数据需要转化成JSON格式
  }else {
    console.log('Illegal Method:'+method);
    return fasle;
  }
};

var expend_editor = document.getElementById("editor-expend");
var nav_bar = document.getElementById("nav-bar");
var article_list = document.getElementById("article-list");
var editor_area = document.getElementById("editor-area");
var title_controller = document.getElementById("title-controller");
var list_group = document.getElementById("list-group");
var docElm = document.documentElement;
var x_selector = document.getElementById("x-selector");

var notebook_button = document.getElementById("notebook-button");
var tags_button = document.getElementById("tags-button");
var add_button = document.getElementById("add-button");
var article_button = document.getElementById("article-button");
var search_button = document.getElementById("search-button");
var add_button = document.getElementById("add-button");
var buttons = [notebook_button,tags_button,add_button,article_button,search_button];
var editor_title = document.getElementById("editor-title");
var x_selector_list = document.getElementById("x-selector-list");
var selector_item = null;

//数据
var notebooks = [];
var articles = [];
var sorted_articles = {};
var current_notebook_id = -1;
var current_article = undefined;
var current_origin_article = undefined;
var origin_title = "";

//全屏功能
expend_editor.onclick = function(){
  if (expend_editor.dataset['expended'] == 'false')
  {
    close_other_panel();
    expend_editor.dataset['expended'] = 'true';
  }
  else {
    show_other_panel();
    expend_editor.dataset['expended'] = 'false';
  }
};

//控制输入框提交按钮显示消失
//title_controller.onmouseover = function(){
//  hide_submit();
//};
//title_controller.onmouseout = function(){
//  show_submit();
//};

function show_submit(){
  document.getElementById("editor-expend").hidden = true;
  document.getElementById("editor-title-cancle-button").hidden = true;
  document.getElementById("editor-title-submit-button").hidden = true;
};

function hide_submit(){
  document.getElementById("editor-expend").hidden = false;
  document.getElementById("editor-title-cancle-button").hidden = false;
  document.getElementById("editor-title-submit-button").hidden = false;
};

//全屏显示关闭其他控件
function close_other_panel(){
  if (docElm.requestFullscreen) { //W3C
      docElm.requestFullscreen();
  } else if (docElm.mozRequestFullScreen) { //FireFox
      docElm.mozRequestFullScreen();
  } else if (docElm.webkitRequestFullScreen) { //Chrome等
      docElm.webkitRequestFullScreen();
  } else if (docElm.msRequestFullscreen) { //IE 11
      docElm.msRequestFullscreen();
  }
  x_selector.hidden = true;
  setTimeout(function(){nav_bar.hidden = true;},200);
  setTimeout(function(){article_list.hidden = true;},100);
};

//取消全面打开其他控件
function show_other_panel(){
  if (document.exitFullscreen) { //W3C
      document.exitFullscreen();
  } else if (document.mozCancelFullScreen) { //FireFox
      document.mozCancelFullScreen();
  } else if (document.webkitCancelFullScreen) { //Chrome等
      document.webkitCancelFullScreen();
  } else if (document.msExitFullscreen) { //IE 11
      document.msExitFullscreen();
  }
  setTimeout(function(){nav_bar.hidden = false;},100);
  setTimeout(function(){article_list.hidden = false;},200);
};

//nav_bar面板的button的点击事件
//notebook按钮点击
notebook_button.onclick = function(){
    x_selector.hidden=!x_selector.hidden;
    button_current(notebook_button);
};
//article按钮点击
article_button.onclick = function(){
  if(x_selector.hidden==false){
    x_selector.hidden=true;
    article_list.hidden=false;
  }
  else{
        article_list.hidden=!article_list.hidden;
  }
  button_current(article_button);
};


//设置该按钮为当前按钮
function button_current(button){
  var tmp_button = buttons.slice();
  tmp_button.splice(tmp_button.indexOf(button),1);
  if(!button.classList.contains("nav-bnt-current")){
      button.classList.add("nav-bnt-current");
      for(i=0;i<tmp_button.length;i++){
        tmp_button[i].classList.remove("nav-bnt-current");
      }
  }
  else {
    button.classList.remove("nav-bnt-current");
  }
};


//初始化数据
function initial_data(){
  console.log("Ready!")
  get_article();
};

//往控件中添加数据
function fulfill_notebooks(){
  clear_notebook_list();
  for(i=0;i<notebooks.length;i++){
    var t = document.createElement('dt');
    t.className = "selector-item";
    t.id = "selector-item";
    article_nums = 0;
    if(sorted_articles[notebooks[i]["id"]]){
      article_nums = sorted_articles[notebooks[i]["id"]].length;
    }

    t.innerHTML = '<div><div class="selector-item-name">'
                  +notebooks[i]["name"]+
                  '</div><div class="selector-item-description">'
                  + article_nums
                  +'条笔记</div></div>';
    t.dataset.id = notebooks[i]["id"];
    t.dataset.type = "notesbook";
    t.dataset.name = notebooks[i]["name"];
    x_selector_list.appendChild(t);
  }
  children = x_selector_list.children;
  // 注意这里需要使用闭包处理!!!
  //设置每个notebook按钮的click事件
  if(children){
    for(i=0;i<children.length;i++){
      children[i].onclick = (function close(j){
        return function() {
          current_notebook_id = children[j].dataset["id"];
          fulfill_articles(children[j].dataset);
          button_current(article_button);
          article_list.hidden = false;
          x_selector.hidden = true;
        }
      })(i);
    };
  };
};

//把文章按照笔记本排序
function sort_article(){
  sorted_articles = [];
  for(i=0;i<articles.length;i++){
    var notebook_id = articles[i]['notebook_id'];
    if(sorted_articles[notebook_id]){
      sorted_articles[notebook_id] = sorted_articles[notebook_id].concat(articles[i]);
    }
    else{
      sorted_articles[notebook_id] = [articles[i]];
    }
  }
};

function fulfill_articles(dataset){
  head_block = document.getElementById("head-block");
  head_block.innerHTML = dataset.name;
  clear_article_list();
  res = sorted_articles[dataset.id];
  if(res){
    for(i=0;i<res.length;i++){
      var t = document.createElement('li');
      t.className = 'list-group-item';
      t.id = 'list-group-item';
      t.innerText = res[i]["title"];
      t.dataset.id = res[i]["id"];
      t.dataset.type = "article";
      list_group.appendChild(t);
      //绑定点击文章按钮
      t.onclick = (function close(j){
        return function() {
          set_current_article(j);
        }
      })(t);
    };
    if(current_article == null)
    {
      set_current_article(list_group.children[0]);
    }
    else {
      article_items = Array.prototype.slice.call(list_group.children);
      var m = article_items.filter(item=>item.dataset.id==current_article.dataset.id);
      if(m.length>0){
        set_current_article(m[0]);
      }
    }
  }
};

function get_article_details(article_id){
  for(i=0;i<articles.length;i++){
    if(articles[i]['id']==article_id){
      return articles[i];
    }
  }
  return {
    "id":undefined,
    "title":"",
    "content":"",
    "source":"",
    "notebook_id":current_notebook_id,
  };
};

//为文章的列表添加onclick事件
//设置该文章为当前选中文章
function set_current_article(article_item){
  if(current_article!=null && current_article.dataset.type=="new_article")
  {
    post_article();
  }
  else if(current_article!=null && (editor.getMarkdown() != current_origin_article || editor_title.value != origin_title))
  {
    console.log('put');
    update_article();
  };
  article = get_article_details(article_item.dataset.id);
  editor_title.value = article["title"];
  editor_title.dataset.id = article["id"];
  editor_title.dataset.type = "article";
  editor.setMarkdown(article["content"]);
  article_items = Array.prototype.slice.call(list_group.children);
  var tmp_articles_items = article_items.slice();
  tmp_articles_items.splice(tmp_articles_items.indexOf(article_item),1);
  if(!article_item.classList.contains("list-group-item-current")){
      article_item.classList.add("list-group-item-current");
      for(i=0;i<tmp_articles_items.length;i++){
        tmp_articles_items[i].classList.remove("list-group-item-current");
      }
  }
  current_article = article_item;
  current_origin_article = editor.getMarkdown();
  origin_title = editor_title.value;
};

function get_notebooks(){
  var ajax = new Ajax({
    method:'get',
    url:'/notebook/get',
    callback:function(res){
      notebooks = JSON.parse(res);
      if(notebooks.length > 0){
        fulfill_notebooks();
        fulfill_articles(notebooks[0]);
        current_notebook_id = notebooks[0]["id"];
      }
    },
    data: {}
  });
  ajax.send();
};

function get_article(notebook_id){
  url_get = '/article/get?limit=10000';
  if(notebook_id>0){
    url_get = url_get + '?notebook_id=' +notebook_id;
    current_notebook_id = notebook_id;
  }
  var ajax = new Ajax({
    method:'get',
    url:url_get,
    callback:function(res){
      articles = JSON.parse(res);
      sort_article();
      get_notebooks();
    },
    data: {}
  });
  ajax.send();
};

function clear_article_list(){
  var children = list_group.children;
  nums = children.length;
  for (i=0;i<nums;i++) {
    list_group.removeChild(children[0]);
  };
};
function clear_notebook_list(){
  var children = x_selector_list.children;
  nums = children.length;
  for (i=0;i<nums;i++) {
    x_selector_list.removeChild(children[0]);
  };
};

function get_title(){
  title = document.getElementById("editor-title")
  return String(title.value);
};
function get_content(){
  content = editor.getMarkdown();
  return String(content);
};
function get_notebook_id(){
  return String(current_notebook_id);
};
function get_article_id(){
  return String(editor_title.dataset.id);
};

function update_article(){
  if(get_article_id()!="undefined") {
    var ajax = new Ajax({
      method:'put',
      url: '/article/put',
      callback:function(res){
        get_article();
        console.log(res);
      },
      data: {
        "id":get_article_id(),
        "content":get_content(),
        "title":get_title(),
        "notebook_id":get_notebook_id(),
      }
    });
    ajax.send();
  }
  else{
    console.log("error:no article id");
  }
};

function post_article(){
  if (get_article_id()=="undefined"){
    var ajax = new Ajax({
      method:'post',
      url:'/article/post',
      callback:function(res){
        console.log(res);
        get_article();
        editor_title.dataset.type="article";
        current_article.dataset.type="article";
      },
      data: {
  	    "title":get_title(),
  	    "content":get_content(),
        "notebook_id":get_notebook_id(),
      }
    });
    ajax.send();
  }
  else{
    console.log("error:already have article id");
  }
};

add_button.onclick = function(){
  if(x_selector.hidden==false){
    new_notebook();
  }
  else{
    new_article();
  };
};

function post_notebook(t,notebook_name){
  var ajax = new Ajax({
    method:'post',
    url:'/notebook/post',
    callback:function(res){
      res = JSON.parse(res);
      console.log(res);
      t.dataset.id = res["id"];
      t.dataset.type = "notesbook";
      t.dataset.name = res["name"];
      fulfill_articles(res);
    },
    data: {
      "name":notebook_name,
    }
  });
  ajax.send();
};


function new_notebook(){
  var t = document.createElement('dt');
  t.className = "selector-item";
  t.id = "selector-item";
  var t_div = document.createElement("div");
  var t_input = document.createElement("input");
  t_input.className = "selector_input";


  var t_des_div = document.createElement("div");
  t_des_div.className = "selector-item-description";
  t_des_div.hidden = true;

  var selector_item = document.createElement("div");
  selector_item.className = "selector-item-name";
  selector_item.hidden = true;
  t.append(t_div);
  t_div.append(t_input);
  t_div.append(selector_item);
  t_div.append(t_des_div);
  //t.innerHTML = '<div><input class="selector_input"><div class="selector-item-name">'
  //              +'</div>'+'</div>';

  //输入框焦点丢失
  t_input.onblur = function(){
    t_input.hidden = true;
    selector_item.hidden = false;
    selector_item.innerText = t_input.value;
    notebook_name = t_input.value;
    post_notebook(t,notebook_name);
    t_des_div.innerText = '0条笔记';
    t_des_div.hidden = false;
  };

  selector_item.onclick = function() {
      current_notebook_id = t.dataset["id"];
      fulfill_articles(t.dataset);
      button_current(article_button);
      article_list.hidden = false;
      x_selector.hidden = true;
    };
  x_selector_list.appendChild(t);
};

editor_title.oninput = function(){
  current_article.innerText = editor_title.value;
};

function new_article(){
  if(editor_title.dataset.type != "new_article"){
    set_current_article(current_article);
  };

  var t = document.createElement('li');
  t.className = 'list-group-item';
  t.id = 'list-group-item';
  t.dataset.type = "new_article";
  list_group.appendChild(t);

  editor_title.value = "";
  editor_title.dataset.id = undefined;
  editor_title.dataset.type = "new_article";
  set_current_article(t);
};
