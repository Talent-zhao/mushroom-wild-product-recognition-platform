/**
 * 覆盖 django-simpleui 自带 menu.js：
 * - 「商品信息管理」分组默认展开（default-openeds）
 * - unique-opened 设为 false，打开其它分组时不会自动收起，便于保持展开直至手动点击收起
 */
Vue.component('sub-menu', {
    props: ['menus', 'fold'],
    methods: {
        openTab(data) {
            window.app.openTab(data);
        }
    },
    template: `
        <div>
            <template v-for="(item,i) in menus" :key="item.eid">
                <el-menu-item  :index="item.eid" v-if="!item.models" @click="openTab(item,item.eid)">
                    <i :class="'menu-icon '+item.icon"></i>
                    <span>{{item.name}}</span>
                </el-menu-item>
                <el-submenu :index="item.eid" v-else>
                    <template slot="title">
                        <i :class="'menu-icon '+item.icon"></i>
                        <span v-show="!fold">{{item.name}}</span>
                    </template>
                   <sub-menu :menus="item.models"></sub-menu>
                </el-submenu>
            </template>
        </div>
    `

});

Vue.component('multiple-menu', {
    props: ['menus', 'menuActive', 'fold'],
    computed: {
        /** 与 app.apps.AppConfig.verbose_name 一致：默认展开该应用下所有子菜单 */
        defaultOpenSubmenus: function () {
            var ids = [];
            if (!this.menus) {
                return ids;
            }
            for (var i = 0; i < this.menus.length; i++) {
                var it = this.menus[i];
                if (it.models && it.name === '商品信息管理') {
                    ids.push(String(it.eid));
                }
            }
            return ids;
        }
    },
    template: `
     <el-menu
        :unique-opened="false"
        :default-openeds="defaultOpenSubmenus"
        :default-active="menuActive"
        :collapse="fold"
        :collapse-transition="true">
        <sub-menu :menus="menus" :fold="fold"></sub-menu>
    </el-menu>
    `
});
