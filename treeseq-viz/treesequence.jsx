import { types } from "mobx-state-tree" // alternatively, `import { t } from "mobx-state-tree"`

const ViewModel = types
  .model("ViewModel", {
    newick: types.string
  })
  .actions(self => ({
    
    update_newick(new_newick_string) {
      self.newick = new_newick_string
    }
  }));


const ConfigModel = types.model("ConfigModel", {
  view: ViewModel
});

export default ConfigModel;