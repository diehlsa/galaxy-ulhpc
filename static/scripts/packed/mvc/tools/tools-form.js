define(["mvc/ui/ui-portlet","mvc/ui/ui-misc","mvc/citation/citation-model","mvc/citation/citation-view","mvc/tools","mvc/tools/tools-template","mvc/tools/tools-datasets","mvc/tools/tools-section","mvc/tools/tools-tree"],function(g,k,i,a,f,d,h,j,c){var e=Backbone.Model.extend({initialize:function(l){this.url=galaxy_config.root+"api/tools/"+l.id+"?io_details=true"}});var b=Backbone.View.extend({main_el:"body",initialize:function(m){var l=this;this.options=m;this.model=new e({id:m.id});this.tree=new c(this);this.field_list={};this.input_list={};this.datasets=new h({history_id:this.options.history_id,success:function(){l._initializeToolForm()}})},_initializeToolForm:function(){var m=this;var n=new k.ButtonIcon({icon:"fa-question-circle",title:"Question?",tooltip:"Ask a question about this tool (Biostar)",onclick:function(){window.open(m.options.biostar_url+"/p/new/post/")}});var o=new k.ButtonIcon({icon:"fa-search",title:"Search",tooltip:"Search help for this tool (Biostar)",onclick:function(){window.open(m.options.biostar_url+"/t/"+m.options.id+"/")}});var l=new k.ButtonIcon({icon:"fa-share",title:"Share",tooltip:"Share this tool",onclick:function(){prompt("Copy to clipboard: Ctrl+C, Enter",galaxy_config.root+"root?tool_id="+m.options.id)}});this.model.fetch({error:function(p){console.debug("tools-form::_initializeToolForm() : Attempt to fetch tool model failed.")},success:function(){m.inputs=m.model.get("inputs");m.portlet=new g.View({icon:"fa-wrench",title:"<b>"+m.model.get("name")+"</b> "+m.model.get("description"),buttons:{execute:new k.ButtonIcon({icon:"fa-check",tooltip:"Execute the tool",title:"Execute",floating:"clear",onclick:function(){m._submit()}})},operations:{button_question:n,button_search:o,button_share:l}});if(!m.options.biostar_url){n.$el.hide();o.$el.hide()}m.message=new k.Message();m.portlet.append(m.message.$el);$(m.main_el).append(m.portlet.$el);if(m.options.help!=""){$(m.main_el).append(d.help(m.options.help))}if(m.options.citations){$(m.main_el).append(d.citations());var p=new i.ToolCitationCollection();p.tool_id=m.options.id;var q=new a.CitationListView({collection:p});q.render();p.fetch()}m.setElement(m.portlet.content());m.section=new j.View(m,{inputs:m.model.get("inputs")});m.portlet.append(m.section.$el);m.refresh();m._submit()}})},refresh:function(){this.tree.refresh();for(var l in this.field_list){this.field_list[l].trigger("change")}console.debug("tools-form::refresh() - Recreated tree structure. Refresh.")},_submit:function(){console.log(this.tree.finalize())}});return{View:b}});