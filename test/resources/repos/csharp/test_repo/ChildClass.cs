using System;

namespace TestRepo
{
    public class ChildClass : BaseClass
    {
        private int value;

        public ChildClass(string name, int value) : base(name)
        {
            this.value = value;
        }

        public override void Execute()
        {
            Console.WriteLine($"Executing {name} with value {value}");
        }

        public int GetValue()
        {
            return value;
        }
    }
}